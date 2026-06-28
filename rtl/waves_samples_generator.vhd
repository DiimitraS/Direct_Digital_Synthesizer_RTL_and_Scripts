-- ******************************************************
-- File name: wave_samples_generator.vhd
-- Description: This unit outputs the sample values of 
--              the wave we want to create
-- ******************************************************
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.sine_table_pkg.all;

entity wave_samples_generator is
    
    generic (
    -- ******************************************************
    -- Parameters
    -- ******************************************************
        ADDR_WIDTH:              integer := 14;
        DAC_WIDTH:               integer := 12;
        NUMBER_WAVES_TYPES:      integer := 3;
        TUNING_WORD_WIDTH:       integer := 32;
        TRUNCATION_SIZE:         integer := 18
    );

    port (
    -- ******************************************************
    -- Ports
    -- ******************************************************

    -- Input ports
        clk                     : in  std_logic;
        rst_n                   : in  std_logic;
        phase                   : in  unsigned(TUNING_WORD_WIDTH-1 downto 0);
        quadrant_sel_r          : in  unsigned(1 downto 0);
        rom_addr_masked         : in unsigned(ADDR_WIDTH-3 downto 0);
        fraction_r              : in unsigned(TRUNCATION_SIZE-1 downto 0);
        rom_addr_next_masked    : in unsigned(ADDR_WIDTH-3 downto 0);
        wave_type_r             : in unsigned(NUMBER_WAVES_TYPES-1 downto 0);

    -- Output ports
        wave_sample_value       : out signed(DAC_WIDTH-1 downto 0)
    );

end entity wave_samples_generator;

    -- ******************************************************
    --                     RTL
    -- ******************************************************

architecture rtl of wave_samples_generator is

    -- ******************************************************
    -- Internal singals
    -- ******************************************************

    signal rom_data_a           : unsigned(DAC_WIDTH-2 downto 0);
    signal rom_data_b           : unsigned(DAC_WIDTH-2 downto 0);
    signal delta                : signed(DAC_WIDTH-1 downto 0);
    signal interp_mul           : signed(TRUNCATION_SIZE+DAC_WIDTH downto 0);
    signal interp_offset        : signed(DAC_WIDTH downto 0);
    signal interp_sample        : signed(DAC_WIDTH downto 0);

    signal wave_sample_value_trig   : signed(DAC_WIDTH-1 downto 0);
	signal wave_sample_value_mx 	: signed(DAC_WIDTH-1 downto 0);
    signal sawtooth_wave            : signed(DAC_WIDTH-1 downto 0);
    signal sawtooth_wave_reverse    : signed(DAC_WIDTH-1 downto 0);
    signal sawtooth_wave_mask       : unsigned(DAC_WIDTH-1 downto 0);
    signal square_wave              : signed(DAC_WIDTH-1 downto 0);
    signal triangle_wave            : signed(DAC_WIDTH-1 downto 0);
    signal triangle_mask            : unsigned(DAC_WIDTH-2 downto 0);
    signal triangle_dir             : unsigned(DAC_WIDTH-2 downto 0);

    constant DAC_MAX_VALUE          : unsigned(DAC_WIDTH-1 downto 0) := to_unsigned(2**(DAC_WIDTH)-1,DAC_WIDTH);

begin

-- *********************************
-- * ROM with sine wave (unsigned) *
-- *********************************

    sine_rom : entity work.rom_sync
        generic map(
            DATA_WIDTH      => (DAC_WIDTH-1),
            ADDR_WIDTH      => (ADDR_WIDTH -2),
            TABLE_OF_VALUES => sine_table
        )
        port map(
            clk      => clk,
            rst_n    => rst_n,
            addr_a     => rom_addr_masked,
            addr_b     => rom_addr_next_masked, -- second read on the next sample, used for linear interpolation
            data_out_a => rom_data_a,
            data_out_b => rom_data_b
        );

-- ******************************************************
-- Interpolation
-- ******************************************************

    delta <= signed('0' & rom_data_b) - signed('0' & rom_data_a);
    interp_mul <= delta * signed('0' & fraction_r);
    interp_offset <= resize(shift_right(interp_mul, TRUNCATION_SIZE), DAC_WIDTH+1);
    interp_sample <= signed('0' & rom_data_a) + interp_offset;

-- ******************************************************
-- Handle sign based on quadrant (for sine and cosine)
-- ******************************************************

 -- 1st Quadrant -> 00 : above midpoint, positive amplitude
 -- 1st Quadrant -> 01 : above midpoint, positive amplitude
 -- 1st Quadrant -> 10 : bellow midpoint, negative amplitude
 -- 1st Quadrant -> 11 : bellow midpoint, negative amplitude   

    wave_sample_value_trig <= interp_sample(DAC_WIDTH-1 downto 0) when quadrant_sel_r(1)='0'
                              else -interp_sample(DAC_WIDTH-1 downto 0);

-- Other waves

    -- Sawtooth

    sawtooth_wave <= signed(phase(TUNING_WORD_WIDTH-1 downto TUNING_WORD_WIDTH-DAC_WIDTH));

    sawtooth_wave_mask <= DAC_MAX_VALUE;

    sawtooth_wave_reverse <= signed(unsigned(phase(TUNING_WORD_WIDTH-1 downto TUNING_WORD_WIDTH-DAC_WIDTH)) xor sawtooth_wave_mask);

    -- Triangle

    triangle_mask <= phase(TUNING_WORD_WIDTH-2 downto TUNING_WORD_WIDTH-DAC_WIDTH);
    
    triangle_dir <= (others => phase(TUNING_WORD_WIDTH-1));

    triangle_wave <= signed('0' & (triangle_mask xor triangle_dir));

    -- Square

    process(phase)
    begin
        if phase(TUNING_WORD_WIDTH-1) = '1' then
            square_wave <= to_signed((2**DAC_WIDTH-1)-1, DAC_WIDTH);
        else
            square_wave <= to_signed(-(2**(DAC_WIDTH-1)-1), DAC_WIDTH);
        end if;
    end process;

    process(wave_type_r,phase,wave_sample_value_trig,sawtooth_wave,square_wave, sawtooth_wave_reverse, triangle_wave)
    begin
        wave_sample_value_mx <= wave_sample_value_trig;
        
        if (wave_type_r = "010") then
            wave_sample_value_mx <= sawtooth_wave;
        elsif (wave_type_r = "011") then
            wave_sample_value_mx <= square_wave;
        elsif (wave_type_r = "100") then
            wave_sample_value_mx <= sawtooth_wave_reverse;
        elsif (wave_type_r = "101") then
            wave_sample_value_mx <= triangle_wave;
        else
            wave_sample_value_mx <= wave_sample_value_trig;
        end if;
    end process;
	
	process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                wave_sample_value <= (others => '0');
            else
                wave_sample_value <= wave_sample_value_mx;
            end if;
        end if;
    end process;

end architecture rtl;
