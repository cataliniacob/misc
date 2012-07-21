#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: $0 <issue_number>"
	exit 1
fi

echo "Cloning to issue$1 ..." && \
hg clone upstream "issue$1" && \
cd "issue$1" && \
echo "Creating branch issue$1 ..." && \
hg branch "issue$1" && \
echo "Changing push to bitbucket" && \
echo 'default-push = ssh://hg@bitbucket.org/cataliniacob/cpython' >>.hg/hgrc && \
echo "Done"
