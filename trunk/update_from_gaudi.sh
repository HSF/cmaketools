#!/bin/bash
#
# Simple script to update the LbUtils copy of the script env.py in Gaudi.
#

git_root=/afs/cern.ch/sw/Gaudi/git/Gaudi.git

# Check if we have all the commands we need.
for c in git patch ; do
    if which $c >/dev/null 2>&1 ; then
	# good
	true
    else
	echo "Cannot find required command '$c'."
	exit 1
    fi
done

# Chech if we can access the Gaudi GIT repository from AFS.
if [ ! -d ${git_root} ] ; then
    echo "This script must be run from a machine with access to AFS."
    exit 1
fi

# Find ourselves (for the destination location)
rootdir=$(dirname $0)

# Get the id of the latest commit in the repository.
if [ -n "$1" ] ; then
    remote_id=$(cd $git_root ; git log -1 --format=%H "$1")
else
    remote_id=$(cd $git_root ; git log -1 --format=%H master)
fi

version_file=$rootdir/.gaudi.version
notes_file=$rootdir/gaudi.notes

# Check if we do have a commit hash of a local copy.
if [ ! -r $version_file ] ; then
    echo "Importing the files from commit ${remote_id}"
    # clean checkout
    git archive --remote=$git_root ${remote_id} cmake/modules cmake/toolchain | \
	tar -x -v -C $rootdir --strip-components=1 -f -
    # create release notes
    (
	cd /afs/cern.ch/sw/Gaudi/git/Gaudi.git
	git log ${remote_id} -- cmake/modules cmake/toolchain
    ) > $notes_file
    # Remember the version of the latest update
    echo ${remote_id} > $version_file
else
    local_id=$(cat $version_file)
    if [ "${remote_id}" == "${local_id}" ] ; then
	echo "Already at the latest version."
    else
	echo "Applying differences for ${local_id}..${remote_id}"
        # apply patches
	(cd $git_root ; git diff ${local_id}..${remote_id} -- cmake/modules cmake/toolchain ) | \
	    (cd $rootdir ; patch -p2)
	# update release notes
	mv $notes_file $notes_file.tmp
	(
	    cd /afs/cern.ch/sw/Gaudi/git/Gaudi.git
	    git log ${local_id}..${remote_id} -- cmake/modules cmake/toolchain
	) > $notes_file
	cat $notes_file.tmp >> $notes_file
	rm $notes_file.tmp
    # Remember the version of the latest update
    echo ${remote_id} > $version_file
    fi
fi

