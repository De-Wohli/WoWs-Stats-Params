import os
import zipfile
import zipfile
['.git', '.vs', 'Data', 'lib', 'Tools']

def zipdir(path,ziph):
    abs_src = os.path.abspath(path)
    for root,dirs,files in os.walk(path,topdown=True):
        dirs[:] = [d for d in dirs if d not in [".git","Tools",".vs"]]
        for file in files:
            if file in ['.gitignore','wgapi.txt','Update.zip','DB_Update.zip']:
                pass
            else:
                absname = os.path.abspath(os.path.join(root, file))
                arcname = "WoWs-Stats-Params\\"+absname[len(abs_src) + 1:]
                ziph.write(absname,arcname)


if __name__ == '__main__':
    zipf = zipfile.ZipFile('Update.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.path.join(os.path.dirname(__file__), '../../'), zipf)
    zipf.close()
    zipf = zipfile.ZipFile('DB_Update.zip', 'w', zipfile.ZIP_DEFLATED)
    abs_src = os.path.join(os.path.dirname(__file__), '../../')
    absname = os.path.join(os.path.dirname(__file__), '../../Data/ships_db.sqlite3')
    arcname = "WoWs-Stats-Params\\"+absname[len(abs_src):]
    zipf.write(absname,arcname)
    zipf.close()

