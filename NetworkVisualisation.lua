nodeX = {}
nodeY = {}
nodeDrawn = {}
nodeOutput = {}
nodeID = {}

while true do
	for i = 1, #nodeX do
		nodeX[i] = 0 
		nodeY[i] = 0
		nodeDrawn[i] = 0
		nodeOutput[i] = 0
	end
	
	
	
	
	-- Draw Buttons
	for i = 1, 6 do
    	if i == 1 or i == 2 then
	    	if outputsAbsolute[i] == false then
	    		gui.drawText(220, 4 + 8*i, buttonNames[i], 0xff000000, 0x00000000, 10 )
	  			gui.drawBox(215, 8 + 8*i, 218, 11 + 8*i, 0xff888888, 0x40000000)  
	  		end
	  		if outputsAbsolute[i] == true then
	    		gui.drawText(220, 4 + 8*i, buttonNames[i], 0xff276d1c, 0x00000000, 10 )
	  			gui.drawBox(215, 8 + 8*i, 218, 11 + 8*i, 0xffffffff, 0xffffffff)  
	  		end
	  	end
	  	if i == 3 or i == 4 then
	    	if outputsAbsolute[i+2] == false then
	    		gui.drawText(220, 4 + 8*i, buttonNames[i+2], 0xff000000, 0x00000000, 10 )
	  			gui.drawBox(215, 8 + 8*i, 218, 11 + 8*i, 0xff888888, 0x40000000)  
	  		end
	  		if outputsAbsolute[i+2] == true then
	    		gui.drawText(220, 4 + 8*i, buttonNames[i+2], 0xff276d1c, 0x00000000, 10 )
	  			gui.drawBox(215, 8 + 8*i, 218, 11 + 8*i, 0xffffffff, 0xffffffff)  
	  		end
	  	end
  	end
  	
  	
  	
  	for i = 1, #nodes do	
		nodeID[i] = nodes[i]
	end
	
	for i = 1, 245, 1 do
		if i <= 240 then
			nodeX[i] = 4 + 4 * ((i-1)%16)
			nodeY[i] = 12 + 4 * (math.floor((i-1)/16))
		end
		if i == 241 then
			nodeX[i] = 16*4
			nodeY[i] = 79
		end
		if i >= 242 and i <= 247 then
			nodeX[i] = 215
			nodeY[i] = 8 + 8*(i-241)
		end
	end	
	
	for i = 1, 245, 1 do
		nodeDrawn[i] = true
	end
	
	for i = 246, #nodes do
		nodeDrawn[i] = false
	end
	
	for i = 246, #nodes do 	
		
		if nodeDrawn[i] == false then
			nodeX[i] = 85 + math.floor((i-245)/5)*20 + (i%2)*6 + (i-245)*3
			nodeY[i] = 2 + (((i-245)%5)+1)*10 
			nodeDrawn[i] = true
		end
	end
	
	for i = 1, 240 do
		if tiles[i] == 1 then
			nodeOutput[i] = 1
		end
		if tiles[i] == -1 then
			nodeOutput[i] = -1
		end
		if tiles[i] == 0 then
			nodeOutput[i] = 0
		end
	end
	for i = 242, 245 do
		if outputsAbsolute[i-241] then
			nodeOutput[i] = 1
		else
			nodeOutput[i] = 0
		end
	end

	
	nodeOutput[241] = 1
	
	
	for i = 246, #nodes do
		nodeOutput[i] = 0
	end
	
	
	
	for i = 1, #connections do	
		source = connections[i][1] 
		sink = connections[i][2]
		weight = connections[i][3]
		
		for i = 1, #nodes do
			if nodeID[i] == source then
				sourceNumber = i
			end
			if nodeID[i] == sink then	
				sinkNumber = i
			end
		end
		
		
		if nodeOutput[sourceNumber] == 1 then
			nodeOutput[sinkNumber] = 1
		end
		if nodeOutput[sourceNumber] == 0 then
			nodeOutput[sinkNumber] = 0
		end
		if nodeOutput[sourceNumber] == -1 then
			nodeOutput[sinkNumber] = -1
		end
		
		if nodeDrawn[sourceNumber] and nodeDrawn[sinkNumber] then
			if nodeOutput[sourceNumber] == 0 then 
				if weight >= 0 then
					gui.drawLine(nodeX[sourceNumber]+1, nodeY[sourceNumber]+1, nodeX[sinkNumber]+1, nodeY[sinkNumber]+1, 0x4F00ff00)
				end
				if weight < 0 then 
					gui.drawLine(nodeX[sourceNumber]+1, nodeY[sourceNumber]+1, nodeX[sinkNumber]+1, nodeY[sinkNumber]+1, 0x4Fff0000)
				end
			else
				if weight >= 0 then
					gui.drawLine(nodeX[sourceNumber]+1, nodeY[sourceNumber]+1, nodeX[sinkNumber]+1, nodeY[sinkNumber]+1, 0xFF00ff00)
				end
				if weight < 0 then 
					gui.drawLine(nodeX[sourceNumber]+1, nodeY[sourceNumber]+1, nodeX[sinkNumber]+1, nodeY[sinkNumber]+1, 0xFFff0000)
				end
			end
		end	
	end
	
	
	gui.drawBox(nodeX[241], nodeY[241], nodeX[241]+3, nodeY[241]+3, 0xffffffff, 0xffffffff)  
	
	for i = 246, #nodes do
		if nodeDrawn[i] == true then
			if nodeOutput[i] == 0 then
	  			gui.drawBox(nodeX[i], nodeY[i], nodeX[i]+3, nodeY[i]+3, 0xff888888, 0x40000000)  
	  		end
	  		if nodeOutput[i] == 1 then
	  			gui.drawBox(nodeX[i], nodeY[i], nodeX[i]+3, nodeY[i]+3, 0xffffffff, 0xffffffff)  
	  		end
	  		if nodeOutput[i] == -1 then
	  			gui.drawBox(nodeX[i], nodeY[i], nodeX[i]+3, nodeY[i]+3, 0xff000000, 0xff000000)  
	  		end
  		end
	end

	emu.frameadvance();
end