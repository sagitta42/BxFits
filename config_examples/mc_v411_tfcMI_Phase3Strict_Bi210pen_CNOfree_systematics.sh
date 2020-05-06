ftype=cno
fit=mv
inputs=Phase3Strict
input_path=fitter_input_v411
tfc=MI
penalty=pep,Bi210:10.8:1.3
met=hm
pdfs=pdfs_fixnpmts
var=nhits
emin=136,140,144
emax=946,950,954
rdmin=484,500,516
# cannot be larger than Emax
rdmax=884,900
rdbin=16,8
# have proven to have virtually no effect, save jobs for other more important parameters
#psmin=398,400
#psmax=648,650
#c11sh=6.5,7.0,7.5
shift=Po210,C11
#scan=CNO
nbatch=20
outfolder=mc_v411_tfcMI_Phase3Strict_Bi210pen_CNOfree_systematics_results
