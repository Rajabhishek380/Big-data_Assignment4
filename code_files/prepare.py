import pandas as pd
import yaml
import os

def prepare_predictions(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    csv_files = [file for file in os.listdir(input_folder) if file.endswith('.csv')]

    for file_name in csv_files:
        input_file_path = os.path.join(input_folder, file_name)
        dataframe = pd.read_csv(input_file_path)
        
        # Convert 'DATE' column to datetime and extract month
        dataframe['DATE'] = pd.to_datetime(dataframe['DATE'])
        dataframe['Month'] = dataframe['DATE'].dt.month
        
        # Filter columns with 'Monthly' in their names
        monthly_params = [col.replace('Monthly', '').replace('Temperature', 'DryBulbTemperature') 
                          for col in dataframe.columns if 'Monthly' in col and 'Departure' not in col]

        # Create dataframe with only relevant columns
        df_monthly = dataframe[['Month'] + monthly_params].dropna(how='all', subset=monthly_params)

        # Save to CSV file
        output_file_path = os.path.join(output_folder, file_name.replace('.csv', '_prepare.csv'))
        df_monthly.to_csv(output_file_path, index=False)

        # Save column names to text file
        text_file_path = os.path.join(output_folder, file_name.replace('.csv', '.txt'))
        with open(text_file_path, 'w') as f:
            f.write(','.join(monthly_params))

def main():
    params = yaml.safe_load(open("params.yaml"))
    input_folder = params["data_source"]["temp_dir"]
    output_folder = params["data_prepare"]["dest_folder"]
    
    prepare_predictions(input_folder, output_folder)

if __name__ == "__main__":
    main()

