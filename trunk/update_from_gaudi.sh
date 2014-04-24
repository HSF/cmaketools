#!/bin/bash
#
# Simple script to update the LbUtils copy of the script env.py in Gaudi.
#

git_root=http://git.cern.ch/pub/gaudi.git

# Check if we have all the commands we need.
for c in git ; do
    if which $c >/dev/null 2>&1 ; then
	# good
	true
    else
	echo "Cannot find required command '$c'."
	exit 1
    fi
done

# Find ourselves (for the destination location)
rootdir=$(dirname $0)

# Branch to use.
if [ -n "$1" ] ; then
    remote_id=$1
else
    remote_id=master
fi

notes_file=$rootdir/doc/gaudi_cmake.notes

echo "Clean destination directory"
# we do not remove '.svn' directories (or directories either)
find $rootdir -noleaf -depth -mindepth 1 -type f -not -wholename "*.svn" -not -wholename "*/.git*" -not -name $(basename $0) -not -name .project -not -name "*.cmake" -exec rm -rfv \{} \;

echo "Importing the files from ${remote_id}"
git clone --bare $git_root $rootdir/.gaudi_tmp
git archive --remote=$rootdir/.gaudi_tmp ${remote_id} cmake/env.py cmake/EnvConfig | \
    tar -x -v -C $rootdir/python --strip-components=1 -f -
git archive --remote=$rootdir/.gaudi_tmp ${remote_id} cmake/toolchain cmake/HEPToolsMacros.cmake cmake/InheritHEPTools.cmake cmake/UseHEPTools.cmake | \
    tar -x -v -C $rootdir/heptools --strip-components=1 -f -
git archive --remote=$rootdir/.gaudi_tmp ${remote_id} cmake/modules | \
    tar -x -v -C $rootdir --strip-components=2 -f -

svn_url=http://svn.cern.ch/guest/lhcb/Gauss/trunk/cmake
echo "Importing files from ${svn_url}"
svn export --force $svn_url $rootdir


# create release notes
(
    cd $rootdir/.gaudi_tmp
    git log --date=short --pretty=format:'! %ad - %an (%h)%n%n - %s%n%n%w(80,3,3)%b%n' ${remote_id} -- cmake
) > $notes_file

svn log $svn_url > $rootdir/doc/gauss_cmake.notes

rm -rf $rootdir/.gaudi_tmp
