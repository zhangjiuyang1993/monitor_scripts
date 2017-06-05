#!/bin/bash
PROCNUM=2
LOGDIR='/home/esb2/mon_scripts/eglog/'
EGARRAY=(AEP_OUTBOUND AEP_OUTBOUND_SUB AEP_OUTBOUND_SUB_ADD1 AEP_OUTBOUND_SUB_ADD2 AEP_OUTBOUND_SUB_ADD3)

function checkEGProc
{
    for var in "${EGARRAY[@]}"
    do
        pNum=`cat psStat.tmp | grep ".*${var}$" | wc -l`
        if [ ${pNum} = ${PROCNUM} ]
        then
            status=1
        else
            status=0
        fi
        curTime=`date '+%Y-%m-%d %H:%M:%S'`
        if [ ! -d ${LOGDIR} ]
        then
            mkdir -p ${LOGDIR}
        fi
        echo ${curTime},${var},${status} >> ${LOGDIR}egStat.log
    done
}



for i in `seq 2`
do
    ssh bjlvfei@sbybz3168.sby.ibm.com ps -ef > psStat.tmp
    checkEGProc
    if [ $i -eq 2 ]
    then
        break
    fi
    sleep 29
done

# function checkEGProc
# {
#     for var in "${EGARRAY[@]}" 
#     do
#         pNum=`cat psStat.tmp | grep ".*${var}$" | wc -l`
#         if [ ${pNum} = ${PROCNUM} ]
#         then
#             status=1
#         else
#             status=0
#         fi
#         curTime=`date '+%Y-%m-%d %H:%M:%S'`
#         if [ ! -d ${LOGDIR} ]
#         then
#             mkdir -p ${LOGDIR}
#         fi
#         if [ ${var} == ${EGARRAY[0]} ]
#         then
#             echo ${curTime},${var},${status} >  ${LOGDIR}egStat.log
#         else
#             echo ${curTime},${var},${status} >> ${LOGDIR}egStat.log
#         fi
#     done 
# }


# for i in `seq 1`
# do
#     ssh bjlvfei@sbybz3168.sby.ibm.com ps -ef > psStat.tmp
#     checkEGProc
#     sleep 30 
# done




