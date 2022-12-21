
register_pattern="^.*FaceQuery face not found.*$"
while read -r line; do
	echo read line: $line
	if [[ \"$line\" =~ $register_pattern ]];then
		nfdc face create udp://192.168.236.50:6363 permanent mtu 1420;
	fi
done < <(register-prefix-remote -f udp4://192.168.236.50:6363 -p /pcl/video 2>&1)
