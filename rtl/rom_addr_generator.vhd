-- ******************************************************
-- File name: rom_addr_generator.vhd
-- Description: This unit generates the rom address
--              based on the wave type and phase
-- ******************************************************
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity rom_addr_generator is
    
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
        wave_type               : in  unsigned(NUMBER_WAVES_TYPES-1 downto 0); -- 0-> Sine, 1 -> Cosine, 2 -> Sawtooth, 3-> Square

    -- Output ports
        wave_type_r             : out unsigned(NUMBER_WAVES_TYPES-1 downto 0);
        fraction_r              : out unsigned(TRUNCATION_SIZE-1 downto 0);
        quadrant_sel_r          : out unsigned(1 downto 0);
        rom_addr_masked         : out unsigned(ADDR_WIDTH-3 downto 0);
        rom_addr_next_masked    : out unsigned(ADDR_WIDTH-3 downto 0)
    );

end entity rom_addr_generator;

    -- ******************************************************
    --                     RTL
    -- ******************************************************

architecture rtl of rom_addr_generator is

    -- ******************************************************
    -- Internal singals
    -- ******************************************************

    signal quadrant_sel          : unsigned(1 downto 0); -- We always need the two MSBs of the phase, to determine the quadrant
    signal read_backward         : std_logic;
    signal mem_addr              : unsigned(ADDR_WIDTH-1 downto 0);
    signal rom_addr_forward      : unsigned(ADDR_WIDTH-3 downto 0);
    signal rom_addr_forward_next : unsigned(ADDR_WIDTH-3 downto 0);
    signal rom_addr_mask         : unsigned(ADDR_WIDTH-3 downto 0); -- Mask defining the direction of reading the ROM based on quadrant
    signal fraction              : unsigned(TRUNCATION_SIZE-1 downto 0);


    signal phase_wave_selected      : unsigned(TUNING_WORD_WIDTH-1 downto 0); -- The phase needed for the chosen wave
    signal phase_cosine             : unsigned(TUNING_WORD_WIDTH-1 downto 0); -- Cosine phase

    constant MAX_ADDR_VALUE         : unsigned(ADDR_WIDTH-3 downto 0):= (others => '1'); -- max value -> all bits '1'
    constant PHASE_COS_OFFSET       : unsigned(TUNING_WORD_WIDTH-1 downto 0) := to_unsigned(2**(TUNING_WORD_WIDTH-2),TUNING_WORD_WIDTH); -- Shift sine wave 90 degrees for cosine phase

begin

-- ****************************************************
-- *                Choose wave type                  *
-- * 000 -> Sine wave, 001 -> Cosine, 010 -> Sawtooth *
-- * 011 -> Square , 100 -> Triangle                  *
-- ****************************************************


    phase_wave_selected <= phase_cosine when wave_type="001"
                            else phase;
    
    phase_cosine <= phase + PHASE_COS_OFFSET;

    process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                wave_type_r <= (others => '0');
            else
                wave_type_r <= wave_type;
            end if;
        end if;
    end process;

-- ************************************
-- * Truncation of the phase into     *
-- * the address signal of the memory *
-- ************************************

    mem_addr <= phase_wave_selected(TUNING_WORD_WIDTH-1 downto TRUNCATION_SIZE);
    fraction <= phase_wave_selected(TRUNCATION_SIZE-1 downto 0);

    process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                fraction_r <= (others => '0');
            else
                fraction_r <= fraction;
            end if;
        end if;
    end process;

-- ***********************
-- * Quadrant choice MUX *
-- ***********************

-- Address Mirroring
 -- 1st Quadrant -> 00 : read from first to last memory location
 -- 1st Quadrant -> 01 : read from last to first memory location
 -- 1st Quadrant -> 10 : read from first to last memory location
 -- 1st Quadrant -> 11 : read from last to first memory location

    quadrant_sel <= mem_addr(ADDR_WIDTH-1 downto ADDR_WIDTH-2); -- The two MSBs are used for finding the quadrant
    read_backward <= quadrant_sel(0);

    process(clk)
    begin
        if rising_edge(clk) then
            if rst_n = '0' then
                quadrant_sel_r <= (others => '0');
            else
                quadrant_sel_r <= quadrant_sel;
            end if;
        end if;
    end process;

    rom_addr_forward   <= mem_addr(ADDR_WIDTH-3 downto 0);

    process(rom_addr_forward, read_backward)
    begin
    if read_backward ='0' then
        if rom_addr_forward = MAX_ADDR_VALUE then
            rom_addr_forward_next <= MAX_ADDR_VALUE;
        else
            rom_addr_forward_next <= rom_addr_forward + 1;
        end if;
    else
        if rom_addr_forward = 0 then
            rom_addr_forward_next <= (others => '0');
        else
            rom_addr_forward_next <= rom_addr_forward - 1;
        end if;
    end if;
end process;

    rom_addr_mask <= (others => read_backward);
    rom_addr_masked <= rom_addr_forward xor rom_addr_mask;

    -- For the next sample read, used in interpolation
    rom_addr_next_masked <= rom_addr_forward_next xor rom_addr_mask;

end architecture rtl;
