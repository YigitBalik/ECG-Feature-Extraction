import argparse

def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dataset", type=str, default="ptbdb", choices=["ptbdb", "ptbxl"])
    parser.add_argument("--show_random_delineation", type=bool, default=False, 
                        help="Shows a delinetaion of a random signal from the given dataset (does not process all dataset)")
    parser.add_argument("--raw_data_folder", type=str, default="./data/")
    parser.add_argument("--folded", type=bool, default=True)
    parser.add_argument("--CV_folds", type=int, default=1, choices=[1, 5, 10])
    parser.add_argument("--SMOTE", type=bool, default=False)
    parser.add_argument("--sampling_rate", type=int, default=1000)
    parser.add_argument("--denoising_method", type=str, default="Neurokit", choices=[
                                                                                    "Neurokit", 
                                                                                    "Biosppy", 
                                                                                    "pantompkins1985", 
                                                                                    "hamilton2002", 
                                                                                    "elgendi2010", 
                                                                                    "koka2022"
                                                                                    ])
    parser.add_argument("--r_detector", type=str, default="Neurokit", choices=[
                                                                                "Neurokit", 
                                                                                "pantompkins1985", 
                                                                                "hamilton2002", 
                                                                                "zong2003", 
                                                                                "martinez2004", 
                                                                                "christov2004", 
                                                                                "elgendi2010",
                                                                                "kalidas2017", 
                                                                                "nabian2018", 
                                                                                "rodrigues2021", 
                                                                                "koka2022"
                                                                                ])
    parser.add_argument("--delineation_method", type=str, default="dwt", choices=["dwt", "cwt", "peak"])
    parser.add_argument("--correct_artifacts", type=bool, default=False)
    parser.add_argument("--correct_peaks", type=bool, default=False)
    parser.add_argument("--tolerance", type=float, default=0.05, help="In what tolerence the peaks will be corrected")
    parser.add_argument("--processed_data_folder", type=str, default="./processed/")
    parser.add_argument("--figure_folder", type=str, default="./figs/")

    return parser.parse_args()
    
