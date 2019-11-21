#!/bin/bash
./borexino input_files/PeriodPhase2_FVpep_TFCMZ_c19.root pp/final_nhits_pp_0 fitoptions/fitoptions_gpu-mv-Phase2MZ-pdfs_TAUP2017-nhits-emin92.cfg species_list/species-fit-gpu-mv_CNO-pileup-penalty.icc | tee livia_checks/fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MZ-nhits-emin92_CNO-pileup-penalty-met_hm.log
./borexino input_files/PeriodPhase2_FVpep_TFCMI_c19.root pp/final_nhits_pp_0 fitoptions/fitoptions_gpu-mv-Phase2MI-pdfs_TAUP2017-nhits-emin92.cfg species_list/species-fit-gpu-mv_CNO-pileup-penalty.icc | tee livia_checks/fit-gpu-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin92_CNO-pileup-penalty-met_hm.log
./borexino input_files/PeriodPhase2_FVpep_TFCMI_c19.root pp/final_nhits_pp_0 fitoptions/fitoptions_cno-mv-Phase2MI-pdfs_TAUP2017-nhits-emin140.cfg species_list/species-fit-cno-mv_CNO-pileup-penalty.icc | tee livia_checks/fit-cno-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin140_CNO-pileup-penalty-met_hm.log
./borexino input_files/PeriodPhase2_FVpep_TFCMI_c19.root pp/final_nhits_pp_0 fitoptions/fitoptions_cno-mv-Phase2MI-pdfs_TAUP2017-nhits-emin140.cfg species_list/species-fit-cno-mv_CNO-penalty.icc | tee livia_checks/fit-cno-mv-pdfs_TAUP2017-PeriodPhase2MI-nhits-emin140_CNO-penalty-met_hm.log
./borexino input_files/PeriodPhase2_FVpep_TFCMI_c19.root pp/final_nhits_pp_0 fitoptions/fitoptions_cno-mv-Phase2MI-pdfs_new-nhits-emin140.cfg species_list/species-fit-cno-mv_CNO-penalty.icc | tee livia_checks/fit-cno-mv-pdfs_new-PeriodPhase2MI-nhits-emin140_CNO-penalty-met_hm.log
./borexino input_files/PeriodPhase3_FVpep_TFCMI_c19.root pp/final_nhits_pp_0 fitoptions/fitoptions_cno-mv-Phase3MI-pdfs_new-nhits-emin140.cfg species_list/species-fit-cno-mv_CNO-penalty.icc | tee livia_checks/fit-cno-mv-pdfs_new-PeriodPhase3MI-nhits-emin140_CNO-penalty-met_hm.log