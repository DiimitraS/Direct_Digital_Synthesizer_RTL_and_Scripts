-- ******************************************************
-- File name: rom_sync.vhd
-- Description: A standard dual port ROM memory. It is
--              a constant lookup table. The synthesis 
--              tool will map it to a LUT ROM 
-- ******************************************************

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.rom_types_pkg.all;

entity rom_sync is
    
    generic (
    -- ******************************************************
    -- Parameters
    -- ******************************************************
        DATA_WIDTH:       integer := 12;
        ADDR_WIDTH:       integer := 10;
        TABLE_OF_VALUES : rom_type
    );

    port (
    -- ******************************************************
    -- Ports
    -- ******************************************************

    -- Input ports
        clk      : in  std_logic;
        rst_n    : in  std_logic;
        addr_a   : in  unsigned(ADDR_WIDTH-1 downto 0);
        addr_b   : in  unsigned(ADDR_WIDTH-1 downto 0);

    -- Output ports
        data_out_a : out unsigned(DATA_WIDTH-1 downto 0);
        data_out_b : out unsigned(DATA_WIDTH-1 downto 0)
    );

end entity rom_sync;

    -- ******************************************************
    --                     RTL
    -- ******************************************************

architecture rtl of rom_sync is

    -- ******************************************************
    -- Internal singals
    -- ******************************************************
    signal data_out_a_pre_samp    : unsigned(DATA_WIDTH-1 downto 0);
    signal data_out_b_pre_samp    : unsigned(DATA_WIDTH-1 downto 0);

    constant ROM_DEPTH: integer :=2**ADDR_WIDTH;

    constant table : rom_type := TABLE_OF_VALUES;

begin

    data_out_a_pre_samp <= table(to_integer(addr_a));
    data_out_b_pre_samp <= table(to_integer(addr_b));

    process(clk, rst_n)
    begin
        if(rst_n = '0') then
            data_out_a <= (others => '0');
            data_out_b <= (others => '0');
        elsif rising_edge(clk) then
            data_out_a <= data_out_a_pre_samp;
            data_out_b <= data_out_b_pre_samp;
        end if;
    end process;

end architecture rtl;
