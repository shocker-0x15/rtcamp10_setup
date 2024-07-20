param (
    [string]$CudaInstaller
)

if ($CudaInstaller -ne "") {
    if (!(Test-Path $CudaInstaller)) {
        Write-Error "The file at path $CudaInstaller does not exist."
        exit 1
    }
    # Write-Output "Start to download CUDA Toolkit"
    # Copy-S3Object -BucketName rtcamp10 -Key cuda_12.5.1_555.85_windows.exe -LocalFile $CudaInstaller -Region ap-northeast-1
    # Write-Output "Finished to download CUDA Toolkit"
}

Write-Output "Start to install miscellaneous things."

Invoke-Expression "& {$(Invoke-RestMethod get.scoop.sh)} -RunAsAdmin"
scoop install git
scoop update
scoop bucket add extras

scoop install python@3.11.4

pip install paramiko
pip install numpy
pip install scipy
pip install Pillow

Write-Output "Finished to install miscellaneous things."



Write-Output "Start to install NVIDIA driver"
$Bucket = "nvidia-gaming"
$KeyPrefix = "windows/latest"
$LocalPath = "$home\Desktop\NVIDIA"
$Objects = Get-S3Object -BucketName $Bucket -KeyPrefix $KeyPrefix -Region us-east-1
foreach ($Object in $Objects) {
    $LocalFileName = $Object.Key
    if ($LocalFileName -ne '' -and $Object.Size -ne 0) {
        $LocalFilePath = Join-Path $LocalPath $LocalFileName
        Copy-S3Object -BucketName $Bucket -Key $Object.Key -LocalFile $LocalFilePath -Region us-east-1
    }
}
$err = (Start-Process -FilePath (Get-ChildItem -Path $home\Desktop\NVIDIA\windows\latest\*.exe -File)[0] -ArgumentList "-s" -Wait -NoNewWindow -PassThru).ExitCode
if ($err -ne 0) {
    Write-Error "Failed to install NVIDIA driver"
}
else {
    New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\nvlddmkm\Global" -Name "vGamingMarketplace" -PropertyType "DWord" -Value "2"
    Invoke-WebRequest -Uri "https://nvidia-gaming.s3.amazonaws.com/GridSwCert-Archive/GridSwCertWindows_2023_9_22.cert" -OutFile "$Env:PUBLIC\Documents\GridSwCert.txt"
    Write-Output "Finished to install NVIDIA driver"
}



$NvSmiDir = "C:\Windows\System32\DriverStore\FileRepository\nvgrid*\"
if ($CudaInstaller -ne "") {
    Write-Output "Start to install CUDA Toolkit"
    
    # CUDA Toolkitを-s -nオプションのみでインストールすると既にインストールしたNVIDIAドライバーをCUDA Toolkit内のドライバで上書きされるらしい。
    # そうなるとVulkanが使えなくなるようなので必要そうなライブラリのみを指定してインストールする。
    # https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html
    $err = (Start-Process -FilePath $CudaInstaller -ArgumentList "-s -n cudart_12.5 nvcc_12.5 nvjitlink_12.5 nvrtc_12.5 nvtx_12.5 thrust_12.5 cublas_12.5 cufft_12.5 curand_12.5 cusolver_12.5 cusparse_12.5 npp_12.5 nvjpeg_12.5" -Wait -NoNewWindow -PassThru).ExitCode
    if ($err -ne 0) {
        Write-Error "Failed to install CUDA Toolkit"
    }
    else {
        # CUDA Toolkitからインストールするライブラリを指定すると環境変数が自動的に設定されないのでここで設定する。
        $CudaPath = [Environment]::GetEnvironmentVariable('CUDA_PATH', 'Machine')
        $UserPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
        [Environment]::SetEnvironmentVariable('path', $CudaPath + '\bin;' + $UserPath, 'User')
        Write-Output "Finished to install CUDA Toolkit"

        # CUDA Toolkitをインストールするとnvidia-smiの場所が変わる。
        $NvSmiDir = ".\"
    }
}



# 結果の安定化のためにGPUクロックを固定する。
# https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/optimize_gpu.html
cd $NvSmiDir
$token = Invoke-RestMethod 'http://169.254.169.254/latest/api/token' -Method Put -Headers @{ "X-aws-ec2-metadata-token-ttl-seconds" = 21600 }
$instType = Invoke-RestMethod 'http://169.254.169.254/latest/meta-data/instance-type' -Headers @{ "X-aws-ec2-metadata-token" = $token }
$clocks = ""
if ($instType.Contains("g4dn")) {
    $clocks = "5001,1590"
} elseif ($instType.Contains("g5")) {
    $clocks = "6250,1710"
}
$err = (Start-Process -FilePath nvidia-smi -ArgumentList "-ac",$clocks -Wait -NoNewWindow -PassThru).ExitCode
if ($err -ne 0) {
    Write-Error "Failed to fix GPU clock"
}
Write-Output "Fixed GPU clock"
