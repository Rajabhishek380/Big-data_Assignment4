import pandas as pd
import os
import yaml
from sklearn.metrics import r2_score

def calculate_r2_scores(ground_truth_folder, predicted_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    csv_files = [file for file in os.listdir(ground_truth_folder) if file.endswith('.csv')]
    
    for file_name in csv_files:
        ground_truth_path = os.path.join(ground_truth_folder, file_name)
        predicted_path = os.path.join(predicted_folder, file_name.replace('_prepare.csv', '_process.csv'))
        
        ground_truth_df = pd.read_csv(ground_truth_path).dropna(axis=1, how='all')
        predicted_df = pd.read_csv(predicted_path).dropna(axis=1, how='all')
        
        common_columns = set(ground_truth_df.columns).intersection(predicted_df.columns)
        common_months = set(ground_truth_df['Month']).intersection(predicted_df['Month'])
        
        ground_truth_df = ground_truth_df.dropna(subset=common_columns)
        predicted_df = predicted_df.dropna(subset=common_columns)
        
        ground_truth_df = ground_truth_df[ground_truth_df['Month'].isin(common_months)]
        predicted_df = predicted_df[predicted_df['Month'].isin(common_months)]
        
        r2_scores = []
        for col in common_columns:
            r2_scores.append(r2_score(ground_truth_df[col], predicted_df[col]))
        
        overall_result = 'Consistent' if all(score >= 0.9 for score in r2_scores) else 'Inconsistent'
        
        output_file_path = os.path.join(output_folder, file_name.replace('_prepare.csv', '_r2.txt'))
        with open(output_file_path, 'w') as f:
            f.write(overall_result + '\n')
            f.write(','.join(map(str, r2_scores)))

def main():
    params = yaml.safe_load(open("params.yaml"))
    ground_truth_folder = params["data_prepare"]["dest_folder"]
    predicted_folder = params["data_process"]["dest_folder"]
    output_folder = params["evaluate"]["output"]
    
    calculate_r2_scores(ground_truth_folder, predicted_folder, output_folder)

if __name__ == "__main__":
    main()
