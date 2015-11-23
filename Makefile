
all:
	mpic++ -o player Util.cpp WorkloadFetcher.cpp WorkloadPlayer.cpp player.cpp
	g++ -o player-runtime Util.cpp SimplePattern.cpp player-runtime.cpp 
