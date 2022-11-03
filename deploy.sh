#!/usr/bin/env bash
#dotnet run --project ./UpdateCron/UpdateCron

IFS=$'\n'

pushd classes

cp prefix.py __init__.py

for f in *.tmpl
do
    pref=${f%.tmpl}
    cat ${f} >> __init__.py
    for fn in ${pref}_/*.py
    do
        sed 's/^/    /g' ${fn} >> __init__.py 
    done
done

cat postfix.py >> __init__.py

popd

cat fns/*.py > classes/combined.py

python -m py_compile classes/combined.py

if [[ $? -ne 0 ]] ; then
    echo "**** Failed to compile combined.py ****"
    exit 1
fi

python -m py_compile classes/__init__.py

if [[ $? -ne 0 ]] ; then
    echo "**** Failed to compile __init__.py ****"
    exit 1
fi


#/usr/local/bin/appcfg.py --oauth2 update $1
gcloud config set project devnpfieldapp2
gcloud app deploy $1app.yaml $1index.yaml --version 1
