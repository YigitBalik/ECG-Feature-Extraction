import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import neurokit2 as nk2
import biosppy as bs
import os
from config import args_parser
import warnings

lead2idx = {
    "I": 0, "II": 1, "III": 2, 
    "aVR": 3, "avr": 3, "AVR": 3,
    "aVL": 4, "avl": 4, "AVL": 4,
    "aVR": 4, "avr": 5, "AVF": 5,
    "V1": 6, "V2": 7, "V3": 8, "V4": 9, "V5": 10, "V6": 11
}

idx2lead = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]

def load_data(data_folder, dataset, folded = None, fold = None):
    if dataset == "ptbxl":
        if folded:
            data_folder = os.path.join(data_folder, "10-fold")
            X_fold = np.load(os.path.join(data_folder, "fold-" + str(fold) + "_signals.npy"))
            y_fold = np.load(os.path.join(data_folder, "fold-" + str(fold) + "_labels.npy"))
            patient_info_fold = np.load(os.path.join(data_folder, "fold-" + str(fold) + "_patient_info.npy"))
            return X_fold, y_fold, patient_info_fold

        signals = np.load(os.path.join(data_folder, "signals.npy"), allow_pickle=True)
        labels = np.load(os.path.join(data_folder, "labels.npy"), allow_pickle=True)
        r_peaks = np.load(os.path.join(data_folder, "peaks.npy"), allow_pickle=True)
        likelihoods = np.load(os.path.join(data_folder, "likelihoods.npy"), allow_pickle=True)
        return signals, labels, r_peaks, likelihoods
    elif dataset=="ptbdb":
        signals_train = np.load(os.path.join(data_folder, dataset, "signals_train.npy"), allow_pickle=True)
        labels_train = np.load(os.path.join(data_folder, dataset, "labels_train.npy"), allow_pickle=True)
        patient_info_train = np.load(os.path.join(data_folder, dataset, "patient_info_train.npy"), allow_pickle=True)
        signals_test = np.load(os.path.join(data_folder, dataset, "signals_test.npy"), allow_pickle=True)
        labels_test = np.load(os.path.join(data_folder, dataset, "labels_test.npy"), allow_pickle=True)
        patient_info_test = np.load(os.path.join(data_folder, dataset, "patient_info_test.npy"), allow_pickle=True)
        return signals_train, labels_train, patient_info_train, signals_test, labels_test, patient_info_test
class Extractor:
    def __init__(self, args):
        self.sr = args.sampling_rate # num of samples / sr = seconds
        self.processed_data_folder = args.processed_data_folder
        self.features = {
            "RR_Prev": [],
            "RR_Next": [],
            "RR_Rat": [],
            "PR_Int": [],
            "PR_Seg": [],
            "QRS": [],
            "P_Wave": [],
            "T_Wave": [],
            "T_Left": [],
            "QT": [],
            "QTc": [],
            "ST": [],
            "PT": [],
            "PS": [],
            "I_R": [], "II_R": [], "III_R": [], "aVR_R": [], "aVL_R": [], "aVF_R": [], "V1_R": [], "V2_R": [], "V3_R": [], "V4_R": [], "V5_R": [], "V6_R": [],
            "I_P": [], "II_P": [], "III_P": [], "aVR_P": [], "aVL_P": [], "aVF_P": [], "V1_P": [], "V2_P": [], "V3_P": [], "V4_P": [], "V5_P": [], "V6_P": [],
            "I_Q": [], "II_Q": [], "III_Q": [], "aVR_Q": [], "aVL_Q": [], "aVF_Q": [], "V1_Q": [], "V2_Q": [], "V3_Q": [], "V4_Q": [], "V5_Q": [], "V6_Q": [],
            "I_S": [], "II_S": [], "III_S": [], "aVR_S": [], "aVL_S": [], "aVF_S": [], "V1_S": [], "V2_S": [], "V3_S": [], "V4_S": [], "V5_S": [], "V6_S": [],
            "I_T": [], "II_T": [], "III_T": [], "aVR_T": [], "aVL_T": [], "aVF_T": [], "V1_T": [], "V2_T": [], "V3_T": [], "V4_T": [], "V5_T": [], "V6_T": [],
            "I_PQ": [], "II_PQ": [], "III_PQ": [], "aVR_PQ": [], "aVL_PQ": [], "aVF_PQ": [], "V1_PQ": [], "V2_PQ": [], "V3_PQ": [], "V4_PQ": [], "V5_PQ": [], "V6_PQ": [],
            "I_QR": [], "II_QR": [], "III_QR": [], "aVR_QR": [], "aVL_QR": [], "aVF_QR": [], "V1_QR": [], "V2_QR": [], "V3_QR": [], "V4_QR": [], "V5_QR": [], "V6_QR": [],
            "I_RS": [], "II_RS": [], "III_RS": [], "aVR_RS": [], "aVL_RS": [], "aVF_RS": [], "V1_RS": [], "V2_RS": [], "V3_RS": [], "V4_RS": [], "V5_RS": [], "V6_RS": [],
            "I_ST": [], "II_ST": [], "III_ST": [], "aVR_ST": [], "aVL_ST": [], "aVF_ST": [], "V1_ST": [], "V2_ST": [], "V3_ST": [], "V4_ST": [], "V5_ST": [], "V6_ST": [],
            "I_PS": [], "II_PS": [], "III_PS": [], "aVR_PS": [], "aVL_PS": [], "aVF_PS": [], "V1_PS": [], "V2_PS": [], "V3_PS": [], "V4_PS": [], "V5_PS": [], "V6_PS": [],
            "I_PT": [], "II_PT": [], "III_PT": [], "aVR_PT": [], "aVL_PT": [], "aVF_PT": [], "V1_PT": [], "V2_PT": [], "V3_PT": [], "V4_PT": [], "V5_PT": [], "V6_PT": [],
            "I_QS": [], "II_QS": [], "III_QS": [], "aVR_QS": [], "aVL_QS": [], "aVF_QS": [], "V1_QS": [], "V2_QS": [], "V3_QS": [], "V4_QS": [], "V5_QS": [], "V6_QS": [],
            "I_QT": [], "II_QT": [], "III_QT": [], "aVR_QT": [], "aVL_QT": [], "aVF_QT": [], "V1_QT": [], "V2_QT": [], "V3_QT": [], "V4_QT": [], "V5_QT": [], "V6_QT": [],
            "I_ST_mean": [], "II_ST_mean": [], "III_ST_mean": [], "aVR_ST_mean": [], "aVL_ST_mean": [], "aVF_ST_mean": [], "V1_ST_mean": [], "V2_ST_mean": [], "V3_ST_mean": [], "V4_ST_mean": [], "V5_ST_mean": [], "V6_ST_mean": [],
            "I_ST_std": [], "II_ST_std": [], "III_ST_std": [], "aVR_ST_std": [], "aVL_ST_std": [], "aVF_ST_std": [], "V1_ST_std": [], "V2_ST_std": [], "V3_ST_std": [], "V4_ST_std": [], "V5_ST_std": [], "V6_ST_std": [],
            "Age": [], "Gender": [],
            "Label": []
        }

    def get_beat_fiducials(self, fiducials, idx):
        r_peak = fiducials["ECG_R_Peaks"][idx]
        r_onset = fiducials["ECG_R_Onsets"][idx]
        r_offset = fiducials["ECG_R_Offsets"][idx]

        p_peak = fiducials["ECG_P_Peaks"][idx]
        p_onset = fiducials["ECG_P_Onsets"][idx]
        p_offset = fiducials["ECG_P_Offsets"][idx]

        q_peak = fiducials["ECG_Q_Peaks"][idx]
        s_peak = fiducials["ECG_S_Peaks"][idx]

        t_peak = fiducials["ECG_T_Peaks"][idx]
        t_onset = fiducials["ECG_T_Onsets"][idx]
        t_offset = fiducials["ECG_T_Offsets"][idx]

        return r_peak, r_onset, r_offset, p_peak, p_onset, p_offset, q_peak, s_peak, t_peak, t_onset, t_offset

    
    def extract_from_record(self, denoised_signals, fiducials, label, patient_info):
        for beat in range(1, len(fiducials["ECG_R_Peaks"]) - 2):
            r_peak, r_onset, r_offset, p_peak, p_onset, p_offset, q_peak, s_peak, t_peak, t_onset, t_offset = self.get_beat_fiducials(fiducials, beat)
            if np.isnan(list((r_peak, r_onset, r_offset, p_peak, p_onset, p_offset, q_peak, s_peak, t_peak, t_onset, t_offset))).any():
                continue

            rr_prev = (fiducials["ECG_R_Peaks"][beat] - fiducials["ECG_R_Peaks"][beat - 1]) / self.sr
            rr_next = (fiducials["ECG_R_Peaks"][beat + 1] - fiducials["ECG_R_Peaks"][beat]) / self.sr
            rr_rat = rr_next / rr_prev
            
            pr_int = abs(p_onset - r_onset) / self.sr
            pr_seg = abs(p_offset - r_onset) / self.sr
            qrs = abs(r_onset - r_offset) / self.sr
            p_wave = abs(p_onset - p_offset) / self.sr
            t_wave = abs(t_onset - t_offset) / self.sr
            t_left = abs(t_onset - t_peak) / self.sr
            qt = abs(r_onset - t_offset) / self.sr
            qtc = (qt / np.sqrt(rr_next)) # check here
            st = abs(r_offset - t_onset) / self.sr
            pt = abs(p_onset - t_offset) / self.sr
            ps = abs(p_onset - r_offset) / self.sr


            
            self.features['RR_Prev'].append(rr_prev)
            self.features['RR_Next'].append(rr_next)
            self.features["RR_Rat"].append(rr_rat)
            self.features["PR_Int"].append(pr_int)
            self.features["PR_Seg"].append(pr_seg)
            self.features["QRS"].append(qrs)
            self.features["P_Wave"].append(p_wave)
            self.features["T_Wave"].append(t_wave)
            self.features["T_Left"].append(t_left)
            self.features["QT"].append(qt)
            self.features["QTc"].append(qtc)
            self.features["ST"].append(st)
            self.features["PT"].append(pt)
            self.features["PS"].append(ps)

            f, s = min(r_offset, t_onset), max(r_offset, t_onset) + 1
            for lead in range(12):
                self.features[idx2lead[lead] + "_R"].append(denoised_signals[r_peak,lead])
                self.features[idx2lead[lead] + "_P"].append(denoised_signals[p_peak,lead])
                self.features[idx2lead[lead] + "_Q"].append(denoised_signals[q_peak,lead])
                self.features[idx2lead[lead] + "_S"].append(denoised_signals[s_peak,lead])
                self.features[idx2lead[lead] + "_T"].append(denoised_signals[t_peak,lead])
                self.features[idx2lead[lead] + "_PQ"].append(denoised_signals[p_peak,lead] - denoised_signals[q_peak,lead])
                self.features[idx2lead[lead] + "_QR"].append(denoised_signals[q_peak,lead] - denoised_signals[r_peak,lead])
                self.features[idx2lead[lead] + "_RS"].append(denoised_signals[r_peak,lead] - denoised_signals[s_peak,lead])
                self.features[idx2lead[lead] + "_ST"].append(denoised_signals[s_peak,lead] - denoised_signals[t_peak,lead])
                self.features[idx2lead[lead] + "_PS"].append(denoised_signals[p_peak,lead] - denoised_signals[s_peak,lead])
                self.features[idx2lead[lead] + "_PT"].append(denoised_signals[p_peak,lead] - denoised_signals[t_peak,lead])
                self.features[idx2lead[lead] + "_QS"].append(denoised_signals[q_peak,lead] - denoised_signals[s_peak,lead])
                self.features[idx2lead[lead] + "_QT"].append(denoised_signals[q_peak,lead] - denoised_signals[t_peak,lead])
                self.features[idx2lead[lead] + "_ST_mean"].append(np.mean(denoised_signals[f:s,lead]))
                self.features[idx2lead[lead] + "_ST_std"].append(np.std(denoised_signals[f:s,lead]))
            
            self.features["Age"].append(patient_info[0])
            self.features["Gender"].append(patient_info[1])
            self.features["Label"].append(label)
    
    def get_features(self):
        return self.features

    def save_df(self, name):
        df = pd.DataFrame.from_dict(self.features)
        print(df.isnull())
        df.to_csv(os.path.join(self.processed_data_folder, name + "_extracted_features.csv"), index=False)
        

class Processor:
    def __init__(self, args):
        self.sr = args.sampling_rate
        self.method_denoise = args.denoising_method
        self.method_rpeak = args.r_detector
        self.correct_artifacts = args.correct_artifacts
        self.correct_peaks = args.correct_peaks
        self.tolerance = args.tolerance
        self.method_delineate = args.delineation_method
        self.extractor = Extractor(args)

    def denoise_single_lead(self, signal):
        return nk2.ecg.ecg_clean(signal, sampling_rate = self.sr, method=self.method_denoise)
    
    def denoise_12_leads(self, signals):
        denoised_signals = np.zeros_like(signals)
        for i in range(12):
            denoised_signals[:, i] = self.denoise_single_lead(signals[:, i])
        return denoised_signals
    
    def denoise_dataset(self, dataset):
        return np.array([self.denoise_12_leads(signals) for signals in dataset])
    
    def correct_rpeaks(self, signal, rpeaks):
        return bs.signals.ecg.correct_rpeaks(signal, rpeaks, self.sr, self.tolerance)[0]
    
    def invert_signal(self, signal):
        fixed, is_inverted = nk2.ecg.ecg_invert(signal, sampling_rate = self.sr, show=False)
        return fixed

    def detect_rpeaks(self, denoised_signal):
        rpeaks = nk2.ecg.ecg_peaks(denoised_signal, sampling_rate=self.sr, method=self.method_rpeak, correct_artifacts=self.correct_artifacts)[1]["ECG_R_Peaks"]

        if self.correct_peaks:
            rpeaks = self.correct_rpeaks(denoised_signal, rpeaks, self.tolerance)
        
        return rpeaks
    
    def detect_fiducials(self, denoised_signal, rpeaks = None, show = False, show_type = "all"):

        if rpeaks is None:
            rpeaks = self.detect_rpeaks(denoised_signal)
            if rpeaks[-1] >= 990:
                rpeaks = rpeaks[:-1]

        _, fiducials = nk2.ecg.ecg_delineate(denoised_signal, 
                                             rpeaks, 
                                             sampling_rate=self.sr,
                                             method=self.method_delineate,
                                             show=show,
                                             show_type=show_type)
        plt.show()
        fiducials["ECG_R_Peaks"] = rpeaks

        return fiducials
    
    def process_dataset(self, raw_signals, labels, patient_info):
        for signals, label, info in tqdm(zip(raw_signals, labels, patient_info)):
            denoised_signals = self.denoise_12_leads(signals)

            # Use Lead I to detect fiducials
            fiducials = self.detect_fiducials(denoised_signals[:, 0], show=False)

            self.extractor.extract_from_record(denoised_signals, fiducials, label, info)
        
    
    def save_processed_dataset(self, name):
        self.extractor.save_df(name)


    

    
    

if __name__ == "__main__":
    args  = args_parser()
    
    data_folder = args.raw_data_folder
    processed_data_folder = args.processed_data_folder

    if not os.path.exists(processed_data_folder):
        os.mkdir(processed_data_folder)

    
    if args.dataset == "ptbxl":
        processor = Processor(args)
        if args.CV_folds == 1:
            for fold in range(10):
                signals, labels, patient_info = load_data(data_folder, args.dataset, args.folded, fold)

                if args.show_random_delineation:
                    idx = np.random.randint(0, signals.shape[0])
                    signal = signals[idx, :, 0]
                    print("Label:", labels[idx], "\nAge,gender:", patient_info[idx])
                    processor.detect_fiducials(processor.denoise_single_lead(signal), show=True)
                
                else:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=RuntimeWarning)
                        processor.process_dataset(signals, labels, patient_info)
            
                    if fold == 8:
                        processor.save_processed_dataset("Train")
                        processor = Processor(args)
                    elif fold == 9:
                        processor.save_processed_dataset("Test")

    elif args.dataset == "ptbdb":
        signals_train, labels_train, patient_info_train, signals_test, labels_test, patient_info_test = load_data(data_folder, args.dataset)
        processor = Processor(args)
        if args.show_random_delineation:
            idx = idx = np.random.randint(0, signals_train.shape[0])
            signal = signals_train[idx, :, 0]
            print("Label:", labels_train[idx], "\nAge,gender:", patient_info_train[idx])
            processor.detect_fiducials(processor.denoise_single_lead(signal), show=True)
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                processor.process_dataset(signals_train, labels_train, patient_info_train)
                processor.save_processed_dataset("Train_ptbdb")

                processor = Processor(args)
                processor.process_dataset(signals_test, labels_test, patient_info_test)
                processor.save_processed_dataset("Test_ptbdb")