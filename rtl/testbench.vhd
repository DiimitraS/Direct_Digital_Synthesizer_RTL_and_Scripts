-- ******************************************************
-- File name: dds_tb.vhd
-- Description: A test bench (non synthesizable code, 
--              to generate waves)
-- ******************************************************

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library std;
use std.textio.all;

entity dds_tb is
end entity dds_tb;

architecture tb of dds_tb is

    constant CLK_PERIOD              : time    := 10 ns; -- 100MHz clock frequency
    constant TUNING_WORD_WIDTH       : integer := 32;
    constant WAVE_SAMPLE_VALUE_WIDTH : integer := 12;
    constant TRUNCATION_SIZE         : integer := 20;
    constant NUMBER_WAVES_TYPES      : integer := 3;

    signal clk               : std_logic := '0';
    signal rst_n             : std_logic := '0';
    signal tuning_word       : unsigned(TUNING_WORD_WIDTH-1 downto 0):= (others => '0');
    signal wave_type         : unsigned(NUMBER_WAVES_TYPES-1 downto 0);
    signal wave_sample_value : std_logic_vector(WAVE_SAMPLE_VALUE_WIDTH-1 downto 0);

begin

    -- DUT (Device Under Test)

    dut : entity work.direct_digital_synthesizer_top
        generic map (
        TUNING_WORD_WIDTH       => TUNING_WORD_WIDTH,
        WAVE_SAMPLE_VALUE_WIDTH => WAVE_SAMPLE_VALUE_WIDTH,
        TRUNCATION_SIZE         => TRUNCATION_SIZE,
        NUMBER_WAVES_TYPES      => NUMBER_WAVES_TYPES
        )
        port map (
            clk                 => clk,
            rst_n               => rst_n,
            tuning_word         => tuning_word,
            wave_type           => wave_type,
            wave_sample_value   => wave_sample_value
        );


    -- Clock generation

    clk_process : process
    begin
        while true loop
            clk <= '0';
            wait for CLK_PERIOD/2;
            clk <= '1';
            wait for CLK_PERIOD/2;
        end loop;
    end process;

    -- Stimulus

    stim_proc : process
    begin
        wave_type <= "000";
        rst_n       <=  '0';

        wait for 20 ns;

        rst_n       <= '1';

        -- Set tuning word
        wait for 10 ns;
        tuning_word <= to_unsigned(214748, TUNING_WORD_WIDTH); -- fout 5 kHz, n_samples = 20000
        --tuning_word <= to_unsigned(2147483, TUNING_WORD_WIDTH); -- fout 50 kHz, n_samples = 2000
        --tuning_word <= to_unsigned(4294967, TUNING_WORD_WIDTH); -- fout 100 kHz, n_samples = 1000
        --tuning_word <= to_unsigned(429496729, TUNING_WORD_WIDTH); -- fout 10 MHz, n_samples = 10
        --tuning_word <= to_unsigned(1932735283, TUNING_WORD_WIDTH); -- fout 45 MHz, n_samples = 2 ~ 3

        wait for 1000000 ns;
        wave_type <= "001";

        wait for 1000000 ns;
        wave_type <= "010";

        wait for 1000000 ns;
        wave_type <= "011";

        wait for 1000000 ns;
        wave_type <= "100";

        wait for 1000000 ns;
        wave_type <= "101";

        wait;

    end process;

   process(clk)
       file fout : text open write_mode is "dds_samples.txt";
       variable line_v : line;
   begin

       if rising_edge(clk) then

           write(line_v,to_integer(unsigned(wave_sample_value)));

       writeline(fout,line_v);

   end if;


   end process;

end architecture tb;
