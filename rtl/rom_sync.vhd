-- ******************************************************
-- File name: rom_sync.vhd
-- Description: A standard ROM memory. Essentially it is 
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
        addr     : in  unsigned(ADDR_WIDTH-1 downto 0);

    -- Output ports
        data_out : out unsigned(DATA_WIDTH-1 downto 0)
    );

end entity rom_sync;

    -- ******************************************************
    --                     RTL
    -- ******************************************************

architecture rtl of rom_sync is

    -- ******************************************************
    -- Internal singals
    -- ******************************************************
    signal data_out_pre_samp    : unsigned(DATA_WIDTH-1 downto 0);

    constant ROM_DEPTH: integer :=2**ADDR_WIDTH;

    constant table : rom_type := TABLE_OF_VALUES;

begin

    data_out_pre_samp <= table(to_integer(addr));

    process(clk, rst_n)
    begin
        if(rst_n = '0') then
            data_out <= (others => '0');
        elsif rising_edge(clk) then
            data_out <= data_out_pre_samp;
        end if;
    end process;

end architecture rtl;
