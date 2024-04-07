import pandas as pd
import yaml
import os

def aggregate_data(input_folder, dest_folder, cols_folder):
    os.makedirs(dest_folder, exist_ok=True)
    csv_files = [file for file in os.listdir(input_folder) if file.endswith('.csv')]
    
    for file_name in csv_files:
        input_file_path = os.path.join(input_folder, file_name)
        dataframe = pd.read_csv(input_file_path)
        
        # Convert 'DATE' column to datetime and extract month
        dataframe['DATE'] = pd.to_datetime(dataframe['DATE'])
        dataframe['Month'] = dataframe['DATE'].dt.month
        
        # Get columns from the text file created in prepare.py
        cols_file_path = os.path.join(cols_folder, file_name.replace('.csv', '.txt'))
        with open(cols_file_path, 'r') as f:
            monthly_params = f.read().split(',')
        
        # Filter columns with 'Daily' or 'Monthly' in their names
        daily_params = [col for col in dataframe.columns if 'Daily' in col]
        monthly_params = [col for col in dataframe.columns if 'Monthly' in col]
        
        # Determine which columns to retain for aggregation
        cols_to_be_retained = []
        new_columns = []
        for daily_col in daily_params:
            for monthly_col in monthly_params:
                if (monthly_col in daily_col) or ('Average' in daily_col and (monthly_col.replace('Mean', '').replace('Average', '') in daily_col.replace('Average', ''))):
                    cols_to_be_retained.append(daily_col)
                    new_columns.append(monthly_col)
        
        # Drop rows with missing values in retained columns
        df_filtered = dataframe.dropna(how='all', subset=cols_to_be_retained)[['Month'] + cols_to_be_retained]
        
        # Aggregate data by month and take mean of other columns
        df_aggregated = df_filtered.groupby('Month').mean().reset_index().rename(columns=dict(zip(cols_to_be_retained, new_columns)))
        
        # Save aggregated data to CSV file
        output_file_path = os.path.join(dest_folder, file_name.replace('.csv', '_process.csv'))
        df_aggregated.to_csv(output_file_path, index=True)

def main():
    params = yaml.safe_load(open("params.yaml"))
    input_folder = params["data_source"]["temp_dir"]
    cols_folder = params["data_prepare"]["dest_folder"]
    dest_folder = params["data_process"]["dest_folder"]
    
    aggregate_data(input_folder, dest_folder, cols_folder)

if __name__ == "__main__":
    main()

    main()