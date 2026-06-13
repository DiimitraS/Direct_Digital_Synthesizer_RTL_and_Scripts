-- ******************************************************
-- File name: rom_types_pkg.vhd
-- Description: A package containing a ROM type
-- ******************************************************

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package rom_types_pkg is

    constant DATA_WIDTH : integer := 11;

    type rom_type is array (natural range <>) of unsigned(DATA_WIDTH-1 downto 0);

end package rom_types_pkg;

package body rom_types_pkg is
end package body rom_types_pkg;
