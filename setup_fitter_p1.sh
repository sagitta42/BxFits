ver=v$1

# check if user gave input
if [ $# -eq 0 ]
  then
      echo "[!] Please provide fitter version in the format x.y.z"
      exit 1
fi

printf "~~~\nVersion $ver\n~~~\n"

# Download bx-GooStats
printf "~~~\nDownloading bx-GooStats\n~~~\n"
mkdir bx-GooStats-release
cd bx-GooStats-release
git clone https://github.com/DingXuefeng/bx-GooStats.git
cd bx-GooStats
git checkout $ver
cd ..

# change the version in the install file
inst=bx-GooStats/setup/download_installbx-GooStats.sh
sed -i "4s/.*/ref=${ver}/" $inst

# Download GooStats
printf "~~~\nDownloading GooStats\n~~~\n"
bash bx-GooStats/setup/download_installbx-GooStats.sh 

# copy the second part in the folder we need before GPU messes it up
cp ../setup_fitter_p2.sh .

# Login to GPU cluster
printf "~~~\nLogging into the GPU cluster\n~~~\n"
srun -p develgpus --gres=gpu:1 -A jikp20  -c 40 -N 1 -t 1:00:00  --pty bash
