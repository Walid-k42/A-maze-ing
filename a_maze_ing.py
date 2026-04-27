import sys
from pydantic import ValidationError
from mazegen import MazeTester
from config_parser import MazeConfig, read_and_split

def main() -> None:
    if len(sys.argv) != 2:
        print("Error: Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    filename = sys.argv[1]
    valid_data = read_and_split(filename)

    if not valid_data:
        return

    try:
        config = MazeConfig(**valid_data)

        tester = MazeTester(config.width, config.height, config.entry, config.exit)
        
        tester.generate() 

        grid = tester._init_ascii_grid()

        tester._apply_walls_to_ascii(grid)

        if grid:
            for row in grid:
                print("".join(row))

    except ValidationError as e:
        clean_msg = e.errors()[0]['msg'].replace("Value error, ", "")
        print(f"Error: {clean_msg}")
    except IndexError:
        print("Error: Coordinates are out of bounds. Check your config file.")

if __name__ == "__main__":
    main()