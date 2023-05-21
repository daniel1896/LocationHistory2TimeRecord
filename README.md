# LocationHistory2TimeRecord

This project allows you to create a time record of a certain location using Google Location History data. The location history data should be downloaded from Google Takeout and represented as a JSON file.

## Usage

To use this project, follow the steps below:

1. Clone the repository to your local machine.

2. Install the required dependencies by running the following command:
```
pip install -r requirements.txt
```

3. Run the main file `main.py` with the necessary arguments:
```
python main.py -i <location_history_file> -lat <target_latitude> -lon <target_longitude> [-o <output_file>] [-r <target_radius>] [-d <minimum_duration>] [-b <break_duration>] [-p]
```
- `-i` or `--input`: Path to the location history file (JSON format).
- `-lat` or `--latitude`: Latitude of the target location.
- `-lon` or `--longitude`: Longitude of the target location.
- `-o` or `--output` (optional): Path to the output file (default: same directory as the input file with the extension changed to `.xlsx`).
- `-r` or `--radius` (optional): Radius of the target location in meters (default: 200).
- `-d` or `--duration` (optional): Minimum duration of the visit in minutes (default: 30).
- `-b` or `--break_duration` (optional): Remove breaks shorter than break_duration (default: None, removes all breaks).
- `-p` or `--print` (optional): Print the time records of the target location.

**Note:** If the input file is not specified, a file dialog will open to select the location history file.

## Example

Here is an example command to create a time record:

```
python main.py -i location_history.json -lat 37.7749 -lon -122.4194 -o time_record.xlsx -r 300 -d 15 -b 60 -p
```

This command will create a time record of the target location with latitude 37.7749 and longitude -122.4194. The location history file is `location_history.json`, and the resulting time record will be saved in `time_record.xlsx`. The target location radius is set to 300 meters, and the minimum duration of the visit is 15 minutes. Breaks shorter than 60 minutes will be removed, and the time records will be printed during the process.

## Output

The resulting time record will be saved in an Excel file with the following columns:

- Date: The date of the visit.
- Start Time: The start time of the visit.
- End Time: The end time of the visit.
- Duration: The duration of the visit.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Please feel free to contribute to this project by opening issues or submitting pull requests.
