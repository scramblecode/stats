import re  # regex
import json 

import json
import re

def extract_player_ids(input_file, output_file):
    """
    Processes player data from an input file and merges it with existing data in an output file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output JSON file.
    """
    try:
        # Initialize empty lists for player data
        player_ids = []
        player_names = []

        # Load existing data from the output file if it exists
        try:
            with open(output_file, 'r') as outfile:
                existing_data = json.load(outfile)
                player_ids = existing_data.get("player_ids", [])
                player_names = existing_data.get("player_names", [])
        except IOError:
            # If the output file doesn't exist, start with empty data
            print("No existing output file found. Starting fresh.")

        # Process the input file for new player data
        with open(input_file, 'r') as infile:
            for line in infile:
                match = re.search(r' connect,(\S+),,(\d+)', line)
                if match:
                    name = match.group(1)
                    player_id = match.group(2)

                    if player_id not in player_ids:
                        # Add new player ID and name
                        player_ids.append(player_id)
                        player_names.append([name])
                    else:
                        # If ID already exists, check for new names
                        index = player_ids.index(player_id)
                        if name not in player_names[index]:
                            player_names[index].append(name)

        # Save the updated data back to the output file
        with open(output_file, 'w') as outfile:
            output_data = {
                "player_ids": player_ids,
                "player_names": player_names,
                "number_of_players": len(player_ids)
            }
            outfile.write(json.dumps(output_data, indent=4, separators=(',', ': ')))
        
        print("Player data successfully updated in the output file.")

        # Print the number of players for confirmation
        print("The total number of players is: %d" % len(player_ids))

    except Exception as e:
        print("An error occurred: %s" % str(e))

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        file_in = sys.argv[1]
        file_out = sys.argv[2]
        extract_player_ids(file_in, file_out)
    else:
        print("Please provide input file and output file as command-line arguments.")