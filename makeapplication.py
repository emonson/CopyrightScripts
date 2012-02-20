### makeapplication.py
from bundlebuilder import buildapp
import os

package_root = '/Users/emonson/Programming/ArtMarkets/CopyrightScripts'

lib_list = []
# lib_list.append(os.path.join(qt_root,'QtCore.framework'))

resource_list = []
# resource_list.append(os.path.join(package_root,'BlankImage.png'))


buildapp(
    name='fashion_ip_gather.app', # what to build
    mainprogram='dump_fashionIP_gsCase_gridFS.py', # your app's main()
    # argv_emulation=1, # drag&dropped filenames show up in sys.argv
    # iconfile='myapp.icns', # file containing your app's icons
    standalone=1, # make this app self contained.
    # encodings.utf_8 is necessary for loading cell arrays of strings
    # includeModules=['encodings.ascii','encodings.utf_8'], # list of additional Modules to force in
    includeModules=['BeautifulSoup','pymongo','httplib2'], # list of additional Modules to force in
    includePackages=[], # list of additional Packages to force in
    resources=resource_list,
    libs=lib_list, # list of shared libs or Frameworks to include
)

### end of makeapplication.py
