### makeapplication.py
from bundlebuilder import buildapp
import os

lib_list = []
# lib_list.append(os.path.join(qt_root,'QtCore.framework'))

resource_list = []
# resource_list.append(os.path.join(package_root,'BlankImage.png'))


buildapp(
    name='test.app', # what to build
    mainprogram='test.py', # your app's main()
    # argv_emulation=1, # drag&dropped filenames show up in sys.argv
    # iconfile='myapp.icns', # file containing your app's icons
    standalone=1, # make this app self contained.
    # encodings.utf_8 is necessary for loading cell arrays of strings
    # includeModules=['encodings.ascii','encodings.utf_8'], # list of additional Modules to force in
    includeModules=[], # list of additional Modules to force in
    includePackages=[], # list of additional Packages to force in
    resources=resource_list,
    libs=lib_list, # list of shared libs or Frameworks to include
)

### end of makeapplication.py
