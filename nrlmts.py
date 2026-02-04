import re  # regex
import json 

import json
import re

##########################################################################################
##MAP START AND END TIMES FT3 ONLY 
def get_match_data(input_file, output_file):

    try:
        matches = []
        try:
            with open(output_file, 'r') as outfile:
                existing_data = json.load(outfile)
                matches = existing_data.get("matches", [])
        except IOError:
            # If the output file doesn't exist, start with empty data
            print("No existing output file found. Starting fresh.")

        start_time = None
        current_map = None
        match_ended = False 
        faction_1 = None
        faction_2 = None 
        lines = []  # Store the previous 3 lines because of map change event before map end 
        rounds = [{
                    "start_time": 0,
                    "players":[],
                    "teams":[],
                    "classes":[],
                    "kills":[],
                    "deaths":[],
                    "weapons":[],
                    "icons":[],
                    "teamkills":[],
                    "teamkilled":[],
                    "tkweapons":[],
                    "tkicons":[],
                    "end_time":[],
                    "flag_time":[],
                    "death_times":[],
                    }]  # 
        
        with open(input_file, 'r') as infile:
            for line in infile:
                lines.append(line)
                if len(lines) > 3:
                    lines.pop(0)  # Keep only the last 3 lines

                # Map Change
                map_change_match = re.search(r'Changed to Battle on (.*?), (.*?) vs (.*?) by .*', lines[-3] if len(lines) > 2 else "")
                if map_change_match:
                    current_map = map_change_match.group(1).strip()
                    faction_1 = map_change_match.group(2).strip()
                    faction_2 = map_change_match.group(3).strip()
                    match_ended = False  # Reset flag
                    

                # Map Start (for match start_time)
                start_match = re.search(r'\s*\[(\d{2}:\d{2}:\d{2})\]\s*msg,\[EVENT\]: Map start.', lines[-1] if lines else "")
                if start_match:
                    start_time = start_match.group(1)
                    rounds = [{
                    "start_time": start_time,
                    "players":[],
                    "teams":[],
                    "classes":[],
                    "kills":[],
                    "deaths":[],
                    "weapons":[],
                    "icons":[],
                    "teamkills":[],
                    "teamkilled":[],
                    "tkweapons":[],
                    "tkicons":[],
                    "end_time":[],
                    "flag_time":[],
                    "death_times":[],
                    }]  
                    match_ended = False  
                # Skip processing if the match has already ended
                if match_ended:
                    continue
                    
                flag_match = re.search(r'^\s*\[(\d{2}:\d{2}:\d{2})\]\s*msg,\[EVENT\]: Flag spawned.', line)
                if flag_match and rounds:
                    rounds[-1]["flag_time"].append(flag_match.group(1).strip())
                
                # Player Data
                player_match = re.search(r'Player:\s*(.*?),\s*Team:\s*(\d)\s*\(.*?\),\s*Class:\s*(.*?)$', line)
                if player_match and rounds:
                    # Append data to respective arrays
                    rounds[-1]["players"].append(player_match.group(1).strip())
                    rounds[-1]["classes"].append(player_match.group(3).strip())
                    rounds[-1]["teams"].append(int(player_match.group(2)))  # Convert team to integer
                    
                # --- Kill events ---
                kill_match = re.search(r'^\s*\[(\d{2}:\d{2}:\d{2})\]\s*kill,(.*?),(.*?),(.*?),(.*?),(.*?)$', line)
                if kill_match and rounds:
                    death_times = kill_match.group(1).strip()
                    killed_name = kill_match.group(2).strip()
                    killer_name = kill_match.group(3).strip()
                    kill_type = kill_match.group(4).strip()
                    weapon_name = kill_match.group(5).strip()
                    hit_bone = kill_match.group(6).strip()
                    rounds[-1]["kills"].append(killer_name)
                    rounds[-1]["deaths"].append(killed_name)                    
                    rounds[-1]["weapons"].append(weapon_name)                    
                    rounds[-1]["death_times"].append(death_times)  
                    if kill_type == "couch":
                        rounds[-1]["icons"].append("ico_couchedlance")
                    elif kill_type == "ranged":
                        rounds[-1]["icons"].append(hit_bone)
                    else:
                        rounds[-1]["icons"].append(weapon_name)
                # weapon icons 
                # ico_match = re.search(r'^\s*\[(\d{2}:\d{2}:\d{2})\]\s*msg,(.*?)\s*<img=(.+?)>\s*(.*?)$', line)
                # if ico_match and rounds:
                    # icon_name = ico_match.group(2).strip()       
                  
                # Teamkills 
                tk_match = re.search(r'^\s*\[(\d{2}:\d{2}:\d{2})\]\s*teamkill,(.*?),(.*?),(.*?),(.*?),(.*?)$', line)
                if tk_match and rounds:
                    # rounds[-1]["tkicons"].append(rounds[-1]["icons"].pop())
                    # rounds[-1]["kills"].pop()
                    tkdeath_times = tk_match.group(1).strip()
                    tkilled_name = tk_match.group(2).strip()
                    tkiller_name = tk_match.group(3).strip()
                    tkkill_type = tk_match.group(4).strip()
                    tkweapon_name = tk_match.group(5).strip()
                    tkhit_bone = tk_match.group(6).strip()
                    rounds[-1]["deaths"].append(tkilled_name)                    
                    rounds[-1]["weapons"].append(tkweapon_name)                    
                    rounds[-1]["death_times"].append(tkdeath_times) 
                    rounds[-1]["teamkills"].append(tkiller_name)                    
                    rounds[-1]["teamkilled"].append(tkilled_name)                    
                    rounds[-1]["tkweapons"].append(tkweapon_name)   
                    if tkkill_type == "couch":
                        rounds[-1]["tkicons"].append("ico_couchedlance")
                    elif tkkill_type == "ranged":
                        rounds[-1]["tkicons"].append(tkhit_bone)
                    else:
                        rounds[-1]["tkicons"].append(tkweapon_name)
                    
                # Round Start (for subsequent rounds)
                round_start_match = re.search(r'\s*\[(\d{2}:\d{2}:\d{2})\]\s*msg,\[EVENT\]: Round start. Score at (.*)', lines[-1] if lines else "")
                if round_start_match:
                    score_match = re.search(r'(\d{1,2}) - (\d{1,2})', round_start_match.group(2))
                    if score_match:
                        score1 = int(score_match.group(1))
                        score2 = int(score_match.group(2))
                        if score1 == 3 or score2 == 3:
                            match_ended = True  # Stop tracking additional rounds
                            # Filter out incomplete rounds
                            valid_rounds = [
                                r for r in rounds if "start_time" in r and "end_time" in r
                            ]
                            if current_map and current_map != "The Cage" and current_map != "The Plank" and current_map != "Tryhard Garden":
                                matches.append({
                                    "start_time": start_time,
                                    "end_time": round_start_match.group(1),
                                    "map": current_map,
                                    "faction_1": faction_1,
                                    "faction_2": faction_2,
                                    "score": round_start_match.group(2).strip(),
                                    "rounds": valid_rounds
                                })
                                
                            start_time = None
                            current_map = None
                            faction_1 = None
                            faction_2 = None
                            rounds = []  # Reset for the next match
                        else:
                            rounds.append({
                            "start_time": round_start_match.group(1),
                            "players":[],
                            "teams":[],
                            "classes":[],
                            "kills":[],
                            "deaths":[],
                            "weapons":[],
                            "icons":[],
                            "teamkills":[],
                            "teamkilled":[],
                            "tkweapons":[],
                            "tkicons":[],
                            "end_time":[],
                            "flag_time":[],
                            "death_times":[],
                            })  # Start a new round

                # Round Result (for round end_time and score check)
                round_result_match = re.search(r'\s*\[(\d{2}:\d{2}:\d{2})\]\s*msg,\[EVENT\]: Round result: (.*)', lines[-1] if lines else "")
                if round_result_match:
                    if rounds:
                        # Add end_time to the latest round
                        rounds[-1]["end_time"] = round_result_match.group(1)
                        rounds[-1]["result"] = round_result_match.group(2).strip()
                    else:
                        # Skip dangling results without valid starts
                        continue
                        
                ###OLIVERAN STATS        
                damage_match = re.search(
                    r'^\s*\[\d{2}:\d{2}:\d{2}\]\s*msg,(.*?)\s+has done\s+(\d+)\s+damage this round,\s+and\s+(\d+)\s+teamdamage this round,\s+and has\s+(\d+)\s+assists',
                    line)
                if damage_match:
                    player_name   = damage_match.group(1).strip()
                    damage_val    = int(damage_match.group(2))
                    teamdamage_val = int(damage_match.group(3))
                    assists_val   = int(damage_match.group(4))
                    
                    # Assume damage info applies to the most recent round that is complete (has an "end_time")
                    if rounds and "end_time" in rounds[-1]:
                        current_round = rounds[-1]
                        # If not already initialized, initialize the parallel arrays with the size of the Players list.
                        if "dmg" not in current_round:
                            current_round["dmg"]      = [0] * len(current_round["players"])
                            current_round["tdmg"]  = [0] * len(current_round["players"])
                            current_round["assists"]     = [0] * len(current_round["players"])
                        try:
                            idx = current_round["players"].index(player_name)
                            current_round["dmg"][idx]     = damage_val
                            current_round["tdmg"][idx] = teamdamage_val
                            current_round["assists"][idx]    = assists_val
                        except ValueError:
                            # If the player's name isn't found in the Players list,
                            # it might be a spectator or extra info that we don't need.
                            pass
                    
                # Map End (to finalize match data)
                #end_match = re.search(r'\s*\[(\d{2}:\d{2}:\d{2})\]\s*msg,\[EVENT\]: Map ended. Score is (.*)', lines[-1] if lines else "")
                #if end_match and start_time:

        # Output results to a JSON file
        with open(output_file, 'w') as outfile:
            outfile.write(json.dumps({"matches":matches}, indent=4, separators=(',', ': ')))

        print("Match dictionaries with rounds written to file.")

    except Exception as e:
        print("An error occurred: {}".format(e))

###########################################################        

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        file_in = sys.argv[1]
        file_out = sys.argv[2]
        get_match_data(file_in, file_out)
        print("Match start-end times recorded.")
    else:
        print("Please provide input file and output file as command-line arguments.")