import pandas as pd
import os
import shutil

def move_files(src_folder, dest_folder):
    # Check if source folder exists
    if not os.path.exists(src_folder):
        print(f"Source folder '{src_folder}' does not exist.")
        return

    # Create destination folder if it doesn't exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Get the list of files in the source folder
    files = os.listdir(src_folder)

    # Move each file to the destination folder
    for file_name in files:
        src_file_path = os.path.join(src_folder, file_name)
        dest_file_path = os.path.join(dest_folder, file_name)

        if not os.path.exists(dest_file_path):
            shutil.copy(src_file_path, dest_file_path)


def move_file(src_folder, src_file, dest_folder, dest_file):
    # Check if source folder exists
    if not os.path.exists(src_folder):
        print(f"Source folder '{src_folder}' does not exist.")
        return

    # Create destination folder if it doesn't exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)


    src_file_path = os.path.join(src_folder, src_file)
    dest_file_path = os.path.join(dest_folder, dest_file)

    if not os.path.exists(dest_file_path):
        shutil.copy(src_file_path, dest_file_path)


def read_csv_to_dataframe(file_path):
    try:
        # Read CSV file into a DataFrame
        df = pd.read_csv(file_path)
        return df

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

# Provide the path to your CSV file
csv_file_path = "data/experimental_design.csv"

# Call the function to read CSV into a DataFrame
data_frame = read_csv_to_dataframe(csv_file_path)

base_folder = 'generated_inputs'
fixed_folder = 'data/default_parameters'
selected_folder = 'data/full_factorial_parameters'
adjusted_folder = 'data/lhs_parameters'

if data_frame is not None:
        # Iterate through each row
        for index, row in data_frame.iterrows():
            # 1. generate input folder name using full factorial
            scen_id = row['scen_id']
            outlook = row['outlook']
            demand = row['demand']
            input_folder = f"input_{scen_id}_{outlook}_{demand}"
            folder_path = os.path.join(base_folder, input_folder)
            # Check if the folder already exists
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Folder created for scen_id {scen_id}: {folder_path}")
            else:
                print(f"Folder already exists for scen_id {scen_id}: {folder_path}")

            # 2.1 move default parameters into target folder
            move_files(fixed_folder, folder_path)
            # 2.2 move full factorial parameters into target folder
            # demand, outlook
            outlook_filename = f"technology_upper_bound_{outlook}.xlsx"
            move_file(selected_folder, outlook_filename, folder_path, "technology_upper_bound.xlsx")
            outlook_filename = f"technology_lower_bound_{outlook}.xlsx"
            move_file(selected_folder, outlook_filename, folder_path, "technology_lower_bound.xlsx")
            demand_filename = f"demand_{demand}.xlsx"
            move_file(selected_folder, demand_filename, folder_path, "demand.xlsx")
            
            # 2.3 move LHS parameters into target folder
            # carbon_offset_price, carbon_offset_limit, reserve_margin
            # fuel_price, fuel_price
            carbon_offset_price = row['carbon_offset_price'] 
            carbon_offset_price_2020 = carbon_offset_price
            carbon_offset_price_2025 = carbon_offset_price
            carbon_offset_price_2030 = carbon_offset_price
            carbon_offset_price_2035 = carbon_offset_price
            carbon_offset_price_2040 = carbon_offset_price
            carbon_offset_price_2045 = carbon_offset_price
            carbon_offset_price_2050 = carbon_offset_price

            carbon_offset_price_filename = os.path.join(adjusted_folder, f"carbon_offset_price.xlsx")
            carbon_offset_price = pd.read_excel(carbon_offset_price_filename)
            carbon_offset_price.loc[carbon_offset_price['zone'] == 2020, 'Singapore'] = carbon_offset_price_2020
            carbon_offset_price.loc[carbon_offset_price['zone'] == 2025, 'Singapore'] = carbon_offset_price_2025
            carbon_offset_price.loc[carbon_offset_price['zone'] == 2030, 'Singapore'] = carbon_offset_price_2030
            carbon_offset_price.loc[carbon_offset_price['zone'] == 2035, 'Singapore'] = carbon_offset_price_2035
            carbon_offset_price.loc[carbon_offset_price['zone'] == 2040, 'Singapore'] = carbon_offset_price_2040
            carbon_offset_price.loc[carbon_offset_price['zone'] == 2045, 'Singapore'] = carbon_offset_price_2045
            carbon_offset_price.loc[carbon_offset_price['zone'] == 2050, 'Singapore'] = carbon_offset_price_2050

            output_carbon_offset_price_file_path = os.path.join(folder_path, f"carbon_offset_price.xlsx")
            # output updated parameter file into target folder
            carbon_offset_price.to_excel(output_carbon_offset_price_file_path, index=False)
            
            # Reserve Margin
            reserve_margin_value = row['reserve_margin']

            reserve_margin_filename = os.path.join(adjusted_folder, f"reserve_margin.xlsx")
            reserve_margin = pd.read_excel(reserve_margin_filename)
            reserve_margin.loc[reserve_margin['zone'] == 2020, 'Singapore'] = reserve_margin_value
            reserve_margin.loc[reserve_margin['zone'] == 2025, 'Singapore'] = reserve_margin_value
            reserve_margin.loc[reserve_margin['zone'] == 2030, 'Singapore'] = reserve_margin_value
            reserve_margin.loc[reserve_margin['zone'] == 2035, 'Singapore'] = reserve_margin_value
            reserve_margin.loc[reserve_margin['zone'] == 2040, 'Singapore'] = reserve_margin_value
            reserve_margin.loc[reserve_margin['zone'] == 2045, 'Singapore'] = reserve_margin_value
            reserve_margin.loc[reserve_margin['zone'] == 2050, 'Singapore'] = reserve_margin_value

            output_reserve_margin_file_path = os.path.join(folder_path, f"reserve_margin.xlsx")
            reserve_margin.to_excel(output_reserve_margin_file_path, index=False)
            
            # Carbon Offset Limit
            carbon_offset_limit_value = row['carbon_offset_limit']

            carbon_offset_limit_filename = os.path.join(adjusted_folder, f"carbon_offset_limit.xlsx")
            carbon_offset_limit = pd.read_excel(carbon_offset_limit_filename)
            carbon_offset_limit.loc[carbon_offset_limit['zone'] == 2020, 'Singapore'] = carbon_offset_limit_value
            carbon_offset_limit.loc[carbon_offset_limit['zone'] == 2025, 'Singapore'] = carbon_offset_limit_value
            carbon_offset_limit.loc[carbon_offset_limit['zone'] == 2030, 'Singapore'] = carbon_offset_limit_value
            carbon_offset_limit.loc[carbon_offset_limit['zone'] == 2035, 'Singapore'] = carbon_offset_limit_value
            carbon_offset_limit.loc[carbon_offset_limit['zone'] == 2040, 'Singapore'] = carbon_offset_limit_value
            carbon_offset_limit.loc[carbon_offset_limit['zone'] == 2045, 'Singapore'] = carbon_offset_limit_value
            carbon_offset_limit.loc[carbon_offset_limit['zone'] == 2050, 'Singapore'] = carbon_offset_limit_value

            output_carbon_offset_limit_file_path = os.path.join(folder_path, f"carbon_offset_limit.xlsx")
            carbon_offset_limit.to_excel(output_carbon_offset_limit_file_path, index=False)

            
            fuel_price_filename = os.path.join(adjusted_folder, f"fuel_price.xlsx")
            fuel_price = pd.read_excel(fuel_price_filename)
            fuel_price_hydrogen_import_2025 = 135.0
            base_year = 2025
            annual_change_fuel_price_hydrogen_import = row['annual_change_fuel_price_hydrogen_import']
            b, y, c = fuel_price_hydrogen_import_2025, base_year, annual_change_fuel_price_hydrogen_import
            fuel_price_hydrogen_import_2030 = b * (1 + c) ** (2030 - y)
            fuel_price_hydrogen_import_2035 = b * (1 + c) ** (2035 - y)
            fuel_price_hydrogen_import_2040 = b * (1 + c) ** (2040 - y)
            fuel_price_hydrogen_import_2045 = b * (1 + c) ** (2045 - y)
            fuel_price_hydrogen_import_2050 = b * (1 + c) ** (2050 - y)
            fuel_price.loc[fuel_price['tech'] == 2030, 'Hydrogen Import'] = fuel_price_hydrogen_import_2030
            fuel_price.loc[fuel_price['tech'] == 2035, 'Hydrogen Import'] = fuel_price_hydrogen_import_2035
            fuel_price.loc[fuel_price['tech'] == 2040, 'Hydrogen Import'] = fuel_price_hydrogen_import_2040
            fuel_price.loc[fuel_price['tech'] == 2045, 'Hydrogen Import'] = fuel_price_hydrogen_import_2045
            fuel_price.loc[fuel_price['tech'] == 2050, 'Hydrogen Import'] = fuel_price_hydrogen_import_2050
            
            # Import
            fuel_price_import_from_laos_value = row['fuel_price_import_from_laos']
            fuel_price.loc[fuel_price['tech'] == 2020, 'Import from Laos'] = fuel_price_import_from_laos_value
            fuel_price.loc[fuel_price['tech'] == 2025, 'Import from Laos'] = fuel_price_import_from_laos_value
            fuel_price.loc[fuel_price['tech'] == 2030, 'Import from Laos'] = fuel_price_import_from_laos_value
            fuel_price.loc[fuel_price['tech'] == 2035, 'Import from Laos'] = fuel_price_import_from_laos_value
            fuel_price.loc[fuel_price['tech'] == 2040, 'Import from Laos'] = fuel_price_import_from_laos_value
            fuel_price.loc[fuel_price['tech'] == 2045, 'Import from Laos'] = fuel_price_import_from_laos_value
            fuel_price.loc[fuel_price['tech'] == 2050, 'Import from Laos'] = fuel_price_import_from_laos_value
            
            fuel_price_import_from_vietnam_value = row['fuel_price_import_from_vietnam']
            fuel_price.loc[fuel_price['tech'] == 2020, 'Import from Vietnam'] = fuel_price_import_from_vietnam_value
            fuel_price.loc[fuel_price['tech'] == 2025, 'Import from Vietnam'] = fuel_price_import_from_vietnam_value
            fuel_price.loc[fuel_price['tech'] == 2030, 'Import from Vietnam'] = fuel_price_import_from_vietnam_value
            fuel_price.loc[fuel_price['tech'] == 2035, 'Import from Vietnam'] = fuel_price_import_from_vietnam_value
            fuel_price.loc[fuel_price['tech'] == 2040, 'Import from Vietnam'] = fuel_price_import_from_vietnam_value
            fuel_price.loc[fuel_price['tech'] == 2045, 'Import from Vietnam'] = fuel_price_import_from_vietnam_value
            fuel_price.loc[fuel_price['tech'] == 2050, 'Import from Vietnam'] = fuel_price_import_from_vietnam_value
            
            fuel_price_import_from_indonesia_value = row['fuel_price_import_from_indonesia']
            fuel_price.loc[fuel_price['tech'] == 2020, 'Import from Indonesia'] = fuel_price_import_from_indonesia_value
            fuel_price.loc[fuel_price['tech'] == 2025, 'Import from Indonesia'] = fuel_price_import_from_indonesia_value
            fuel_price.loc[fuel_price['tech'] == 2030, 'Import from Indonesia'] = fuel_price_import_from_indonesia_value
            fuel_price.loc[fuel_price['tech'] == 2035, 'Import from Indonesia'] = fuel_price_import_from_indonesia_value
            fuel_price.loc[fuel_price['tech'] == 2040, 'Import from Indonesia'] = fuel_price_import_from_indonesia_value
            fuel_price.loc[fuel_price['tech'] == 2045, 'Import from Indonesia'] = fuel_price_import_from_indonesia_value
            fuel_price.loc[fuel_price['tech'] == 2050, 'Import from Indonesia'] = fuel_price_import_from_indonesia_value

            fuel_price_import_from_australia_value = row['fuel_price_import_from_australia']
            fuel_price.loc[fuel_price['tech'] == 2020, 'Import from Australia'] = fuel_price_import_from_australia_value
            fuel_price.loc[fuel_price['tech'] == 2025, 'Import from Australia'] = fuel_price_import_from_australia_value
            fuel_price.loc[fuel_price['tech'] == 2030, 'Import from Australia'] = fuel_price_import_from_australia_value
            fuel_price.loc[fuel_price['tech'] == 2035, 'Import from Australia'] = fuel_price_import_from_australia_value
            fuel_price.loc[fuel_price['tech'] == 2040, 'Import from Australia'] = fuel_price_import_from_australia_value
            fuel_price.loc[fuel_price['tech'] == 2045, 'Import from Australia'] = fuel_price_import_from_australia_value
            fuel_price.loc[fuel_price['tech'] == 2050, 'Import from Australia'] = fuel_price_import_from_australia_value

            fuel_price_import_from_cambodia_value = row['fuel_price_import_from_cambodia']
            fuel_price.loc[fuel_price['tech'] == 2020, 'Import from Cambodia'] = fuel_price_import_from_cambodia_value
            fuel_price.loc[fuel_price['tech'] == 2025, 'Import from Cambodia'] = fuel_price_import_from_cambodia_value
            fuel_price.loc[fuel_price['tech'] == 2030, 'Import from Cambodia'] = fuel_price_import_from_cambodia_value
            fuel_price.loc[fuel_price['tech'] == 2035, 'Import from Cambodia'] = fuel_price_import_from_cambodia_value
            fuel_price.loc[fuel_price['tech'] == 2040, 'Import from Cambodia'] = fuel_price_import_from_cambodia_value
            fuel_price.loc[fuel_price['tech'] == 2045, 'Import from Cambodia'] = fuel_price_import_from_cambodia_value
            fuel_price.loc[fuel_price['tech'] == 2050, 'Import from Cambodia'] = fuel_price_import_from_cambodia_value
            
            fuel_price_import_from_malaysia_value = row['fuel_price_import_from_malaysia']
            fuel_price.loc[fuel_price['tech'] == 2020, 'Import from Malaysia'] = fuel_price_import_from_malaysia_value
            fuel_price.loc[fuel_price['tech'] == 2025, 'Import from Malaysia'] = fuel_price_import_from_malaysia_value
            fuel_price.loc[fuel_price['tech'] == 2030, 'Import from Malaysia'] = fuel_price_import_from_malaysia_value
            fuel_price.loc[fuel_price['tech'] == 2035, 'Import from Malaysia'] = fuel_price_import_from_malaysia_value
            fuel_price.loc[fuel_price['tech'] == 2040, 'Import from Malaysia'] = fuel_price_import_from_malaysia_value
            fuel_price.loc[fuel_price['tech'] == 2045, 'Import from Malaysia'] = fuel_price_import_from_malaysia_value
            fuel_price.loc[fuel_price['tech'] == 2050, 'Import from Malaysia'] = fuel_price_import_from_malaysia_value

            output_fuel_price_file_path = os.path.join(folder_path, f"fuel_price.xlsx")
            fuel_price.to_excel(output_fuel_price_file_path, index=False)
            
            # carbon tax
            carbon_tax_filename = os.path.join(adjusted_folder, f"carbon_tax.xlsx")
            carbon_tax = pd.read_excel(carbon_tax_filename)
            carbon_tax_2030 = row['carbon_tax_2030']
            base_year = 2030
            annual_change_carbon_tax = row['annual_change_carbon_tax_2030']
            b, y, c = carbon_tax_2030, base_year, annual_change_carbon_tax
            carbon_tax_2035 = b * (1 + c) ** (2035 - y)
            carbon_tax_2040 = b * (1 + c) ** (2040 - y)
            carbon_tax_2045 = b * (1 + c) ** (2045 - y)
            carbon_tax_2050 = b * (1 + c) ** (2050 - y)
            carbon_tax.loc[carbon_tax['zone'] == 2030, 'Singapore'] = carbon_tax_2030
            carbon_tax.loc[carbon_tax['zone'] == 2035, 'Singapore'] = carbon_tax_2035
            carbon_tax.loc[carbon_tax['zone'] == 2040, 'Singapore'] = carbon_tax_2040
            carbon_tax.loc[carbon_tax['zone'] == 2045, 'Singapore'] = carbon_tax_2045
            carbon_tax.loc[carbon_tax['zone'] == 2050, 'Singapore'] = carbon_tax_2050
            
            output_fuel_price_file_path = os.path.join(folder_path, f"carbon_tax.xlsx")
            carbon_tax.to_excel(output_fuel_price_file_path, index=False)
        print(index)
