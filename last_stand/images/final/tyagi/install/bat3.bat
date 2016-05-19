@echo off
cd C:\dependencies
echo "installing numpy........."
pip install numpy-1.10.4+mkl-cp27-cp27m-win_amd64.whl
echo "installing scipy .........."
pip install scipy-0.17.0-cp27-none-win_amd64.whl
echo "installing scikit-learn"
pip install scikit_learn-0.17.1-cp27-cp27m-win_amd64.whl
echo "installing fastcluster"
pip install fastcluster
CALL bat4.bat
pause
