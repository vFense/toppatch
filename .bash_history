echo PATH
echo $PATH
which python
vim .bashrc 
/usr/bin/vim .bashrc
echo $PATH
ls /usr/games/
vim .bashrc 
ls
vim .bashrc 
/usr/bin/vim .bashrc
ls
rm examples.desktop 
mkdir python
mkdir mysql
mkdir -p python/python-2.7.3/lib
mkdir -p mysql/percona-5.5
tar -xzvf Python-2.7.3.tgz 
cd Python-2.7.3/
./configure --prefix=/opt/TopPatch/python/python-2.7.3 --with-pth --enable-shared LDFLAGS="-Wl,-rpath /opt/TopPatch/python/python-2.7.3/lib"
make
make install
make clean
cd ../
rm -rf Python-2.7.3
ls -ltrh
cd python/
ls -ltrh
ln -s python-2.7.3/ current
ls
cd ../
ls
rm -rf Python-2.7.3.tgz 
vim .bashrc 
mkdir sbin
mkdir bin
history |grep -i cmake
ls
tar -xzvf Percona-Server-5.5.23-rel25.3.tar.gz 
cd Percona-Server-5.5.23-rel25.3/
cmake . -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_CONFIG=mysql_release -DFEATURE_SET=community -DWITH_EMBEDDED_SERVER=OFF -DCMAKE_INSTALL_PREFIX=/home/allen/TopPatch/mysql/Percona-5.5
ls ../
ls ../mysql/
cmake . -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_CONFIG=mysql_release -DFEATURE_SET=community -DWITH_EMBEDDED_SERVER=OFF -DCMAKE_INSTALL_PREFIX=/home/allen/TopPatch/mysql/percona-5.5
make
make install
cd ../
rm -rf Percona-Server-5.5.23-rel25.3
tar -xzvf Percona-Server-5.5.23-rel25.3.tar.gz 
cd Percona-Server-5.5.23-rel25.3/
cmake . -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_CONFIG=mysql_release -DFEATURE_SET=community -DWITH_EMBEDDED_SERVER=OFF -DCMAKE_INSTALL_PREFIX=/opt/TopPatch/mysql/percona-5.5
make
make install
make clean
cd ../
rm -rf Percona-Server-5.5.23-rel25.3
ls
rm -rf Percona-Server-5.5.23-rel25.3.tar.gz 
cd python/
ls -ltrh
cd ../
cd mysql/
ls -ltrh
ln -s percona-5.5/ current
ls -ltr
cd ../
vim .bash
vim .bashrc 
which python
ls
tar -xzvf setuptools-0.6c11.tar.gz 
cd setuptools-0.6c11/
which python
python setup.py install
easy_install pip
cd ../
rm -rf setuptools-0.6c11
easy_install pip
pip install yolk tornado ipaddr python-daemon 
yolk -a
pip search tornado
pip install sqlalchemy
pip install lxml
sudo apt-cache search xml
pip install lxml
yolk -a
ls -ltrh
rm -rf setuptools-0.6c11.tar.gz 
du -sh ./
ls
mkdir toppatch
history |grep git
rm toppatch/
rm -rf toppatch/
https://github.com/toppatch/toppatch.git
git clone https://github.com/toppatch/toppatch.git
pip search sql
pip search network
pip search icmp
