json = require "json"



-- GET FROM FIFO						
ptol = io.open("ptol", "r")
ltop = io.open("ltop", "w")

function readLine()
    local line = ptol:read("*l")
    while line == nil do
        line = ptol:read("*l")
    end
    return json.decode(line)
end

function writeLine(data)
    ltop:write(json.encode(data) .. "\n")
    ltop:flush()
end

completion = false

-- BLOCK 2: INPUTS  
while not completion do
    savestate.loadslot(1)
    -- BLOCK 1: VARIABLE INITIATION

    -- Initiation of the input array (tiles)
    tiles = {}
    for i = 1, 240, 1 do
        tiles[#tiles+1] = 0
    end

    -- Initiation array enemy for-loops
    enemyAlive = {}
    enemyVertical = {}
    enemyHorizontal  = {} 
    EnableEnemyRender = {}

    -- Variables to retain previous frame data
    fireballPrevious1 = 0
    fireballPrevious2 = 0
    fireballSecondPrevious1 = 0
    fireballSecondPrevious2 = 0
    boomarangPrevious1 = 0
    boomarangPrevious2 = 0
    boomarangSecondPrevious1 = 0
    boomarangSecondPrevious2 = 0

    -- Fitness checking
    fitnessPrevious = 0
    fitnessTimer = 0
    fitnessTimer2 = 0

    -- Finish block Y position
    memory.writebyte(0x00A9, 128);

    -- Controller data
    controller = {}
    outputs = {
        false,
        true,
        false,
        true,
        false
    }
    outputsAbsolute = {}
    buttonNames = {
        "A",
        "B",
        "Up",
        "Down",
        "Left",
        "Right"
    }



    data = readLine()
    generation = data["generation"]
    species = data["speciesId"]
    GenProgress = data["genpercent"]
    maxFitness = data["maxFitness"]
    genomeNumber = data["genomeId"]
    nodes = data["nodes"]
    connections = data["connections"]

    fitnessHighest = 0
    oldTime = 0
    time = 0
    
    while true do

            -- Temporary, development only
            -- memory.writebyte(0x000ED, 05) -- Infinite Tanooki power-up
            -- memory.writebyte(0x05F1, 1) -- Disable timer


        -- Draw Input Box - empty
        gui.drawBox(3, 11, 16*4 + 4, 15*4 + 12, 0xff000000 ,0x40000000)
        gui.drawLine(15, 12, 15, 71, 0xff888888)
        gui.drawLine(56, 12, 56, 71, 0xff888888)

        -- Refresh inputs
        for c = 1, 16*16, 1 do
            tiles[c] = 0
        end

        -- Get Mario Coordinates
        marioX = memory.readbyte(0x00090) + memory.readbyte(0x00075) * 256 + 8
        if memory.readbyte(0x00087) ~= 255 then 
            marioY = memory.readbyte(0x000A2) + memory.readbyte(0x00087) * 256
        else
            -- (The vertical Low byte is equal to 255 on the topmost row of the map)
            marioY = 0 
        end

        -- Check all tiles around Mario for hitboxes and update inputs (hitboxes)
        for i = 1, 241, 1 do
            tileX = marioX - 128 + (16*(i-1))%256   
            tileY = marioY - 128 + 16*math.floor((i-1)/16)

            tileHorizontalLow = math.floor(tileX/256)
            tileHorizontalHigh = math.floor((tileX%256)/16)
            if tileY >= 0 then
                tileVertical = math.floor(tileY/16)
            else
                -- Dit is voor dezelfde redenen als bij marioY hierboven
                tileVertical = 0			
            end
            tileData = memory.readbyte(0x6000 + tileHorizontalLow*27*16 + tileHorizontalHigh + tileVertical*16)
            if	tileData == 44  or tileData == 83  or tileData == 85  or tileData == 87  or tileData == 95  or tileData == 97  or tileData == 99  or tileData == 103 or 
                tileData == 110 or tileData == 112 or tileData == 121 or tileData == 173 or tileData == 174 or tileData == 177 or 
                tileData == 178 or tileData == 186 or tileData == 187 or tileData == 37  or tileData == 38  or tileData == 39  or tileData == 80  or 
                tileData == 81  or tileData == 82  or tileData == 160 or tileData == 161 or tileData == 162 or tileData == 226 or tileData == 227 or 
                tileData == 228 or tileData == 46  or tileData ==  49 or tileData == 105 or tileData == 107 or tileData == 109 or tileData == 113 or tileData == 114 or 
                tileData == 116 or tileData == 154 or tileData == 155 or tileData == 156 or tileData == 157 or tileData == 158 or tileData == 167 or tileData == 168 or 
                tileData == 169 or tileData == 170 or tileData == 171 or tileData == 182 or tileData == 183 or tileData == 184 or tileData == 185
            then
                tiles[i] = 1
            end
        end

        -- Update frame-dependent Variables
        screenHorizontalPosition = memory.readbyte(0x00FD) + memory.readbyte(0x0012)*256

        -- Get enemy data
        for i = 1, 5, 1 do
            enemyAlive[i] = memory.readbyte(0x665 - i + 1)

            enemyX = screenHorizontalPosition + memory.readbyte(176 - i + 1) + 8
            enemyHorizontal[i]  = math.floor((enemyX - marioX) / 16) - 7

            enemyY = memory.readbyte(167 - i + 1) + 256
            enemyVertical[i] = math.floor(enemyY / 16) + 9 - math.floor(marioY/16)
        end
       -- Circumvent enemy position overflow - No enemies render outside the two lines
       for i = 1, 5, 1 do 
            if enemyHorizontal[i] < -12 or enemyHorizontal[i] > -3 then
                EnableEnemyRender[i] = 0	
            else
                EnableEnemyRender[i] = 1
            end
        end  
        -- Update inputs (enemies)
        for i = 1, 5, 1 do
            if EnableEnemyRender[i] == 1 then
                if enemyAlive[i] == 2 or enemyAlive[i] == 5 then			
                        tiles[(enemyVertical[i])*16 + enemyHorizontal[i]] = -1
                end
            end
        end

        -- Get Projectile data (fireball)
        fireballHorizontal1  = math.floor((memory.readbyte(0x05CB)+256-marioX)/16)%16 - 6
        fireballHorizontal2  = math.floor((memory.readbyte(0x05CC)+256-marioX)/16)%16 - 6
        fireballVertical1  = math.floor((memory.readbyte(0x05C1) + 256 - marioY)/16) + 9
        fireballVertical2  =  math.floor((memory.readbyte(0x05C2) + 256 - marioY)/16) + 9

        fireballDirection1 = fireballSecondPrevious1 - memory.readbyte(0x05CB)
        fireballSecondPrevious1 = fireballPrevious1
        fireballPrevious1 = memory.readbyte(0x05CB)

        fireballDirection2 = fireballSecondPrevious2 - memory.readbyte(0x05CC)
        fireballSecondPrevious2 = fireballPrevious2
        fireballPrevious2 = memory.readbyte(0x05CC)

        -- Get Projectile data (boomarang)
        boomarangHorizontal1  = math.floor((memory.readbyte(0x05CD)+256-marioX)/16)%16 - 6
        boomarangHorizontal2  = math.floor((memory.readbyte(0x05CE)+256-marioX)/16)%16 - 6
        boomarangVertical1  = math.floor((memory.readbyte(0x05C3) + 256 - marioY)/16) + 9
        boomarangVertical2  =  math.floor((memory.readbyte(0x05C4) + 256 - marioY)/16) + 9

        boomarangDirection1 = boomarangSecondPrevious1 - memory.readbyte(0x05CD)
        boomarangSecondPrevious1 = boomarangPrevious1
        boomarangPrevious1 = memory.readbyte(0x05CD)

        boomarangDirection2 = boomarangSecondPrevious2 - memory.readbyte(0x05CE)
        boomarangSecondPrevious2 = boomarangPrevious2
        boomarangPrevious2 = memory.readbyte(0x05CE)

        -- Update inputs (projectiles)
        if fireballDirection1 ~= 0 then
            tiles[fireballVertical1*16 + fireballHorizontal1] = -1
        end
        if fireballDirection2 ~= 0 then
        tiles[fireballVertical2*16 + fireballHorizontal2] = -1
        end
        if boomarangDirection1 ~= 0 then
            tiles[boomarangVertical1*16 + boomarangHorizontal1] = -1
        end
        if boomarangDirection2 ~= 0 then
        tiles[boomarangVertical2*16 + boomarangHorizontal2] = -1
        end


        -- Draw inputs
        for layer = 1, 15, 1 do
            for i = 1, 16, 1 do
                sqX = 4 + (i-1) * 4
                sqY = 12 + (layer-1) * 4 
                -- Enemies and projectiles
                if tiles[(layer-1)*16+i] == -1 then       
                    gui.drawBox(sqX, sqY, sqX + 3, sqY + 3, 0xFF000000, 0xFF000000)            
                else 
                -- Hitboxes
                if tiles[(layer-1)*16+i] == 1 then
                    gui.drawBox(sqX, sqY, sqX + 3, sqY + 3, 0xffffffff, 0xffffffff)
                else
                -- Empty space
                    gui.drawBox(sqX, sqY, sqX + 3, sqY + 3, 0x000000, 0x000000) 
                end
                end       
            end
        end

        -- Draw position Mario
        gui.drawBox(37, 45, 38, 51, 0xFF740858, 0xFF740858)
        gui.drawLine(34, 51, 41, 51, 0xFF740858)


    -- BLOCK 3: GENOME DATA AND FITNESS

        oldTime = time
        time = memory.readbyte(0x05EE)*100 + memory.readbyte(0x05EF)*10 + memory.readbyte(0x05F0)
        score =  memory.readbyte(0x0717)*10 + memory.readbyte(0x0716)*2560
        fitness = marioX + time + score

	if (marioY >= 400) then
		stuck = true
	end

	if (fitness > fitnessHighest) then
		fitnessHighest = fitness
	end

	if (fitnessHighest > fitness) then
		fitnessTimer2 = fitnessTimer2 + 1
	end

	if (fitnessTimer2 > 6) then
		fitnessTimer2 = 0
		stuck = true
	end

        if oldTime > time then
            fitnessTimer = fitnessTimer + 1;
        elseif (fitnessPrevious - time) < (fitness - time) then
            fitnessTimer = 0;
        end
        if fitnessTimer > 3 then
            stuck = true
        end

	if stuck ==  true then
                writeLine({["noInput"] = 1})
		stuck = false
                break
	end

        fitnessPrevious = fitness;


        if marioX > screenHorizontalPosition + 192 then
            completion = true
            writeLine({["complete"] = 1})
        else
            completion = false
        end 

    -- SEND TO FIFO					
        writeLine({["input"] = tiles})

        data = readLine()
        outputs = data["output"]

        writeLine({["fitness"] = fitness})


        for i = 1, 6 do
            if outputs[i] > 0.9 then
                outputsAbsolute[i] = true
            end
            if outputs[i] < 0.9 then
                outputsAbsolute[i] = false
            end
        end


        gui.drawBox(0,210,255,255, 0x8fffffff, 0xDfffffff)

        gui.drawText(10, 220, "Gen: " .. generation, 0xff000000, 0x00000000, 10)
        gui.drawText(65, 220, "Species: " .. species, 0xff000000, 0x00000000, 10)
        gui.drawText(140, 220, "Genome: " .. genomeNumber, 0xff000000, 0x00000000, 10)
        gui.drawText(210, 220, "(" .. GenProgress .. "%)", 0xff000000, 0x00000000, 10)

        gui.drawText(10, 210, "Fitness: " .. fitness, 0xff000000, 0x00000000, 10)
        gui.drawText(100, 210, "Max Fitness: " .. maxFitness, 0xff000000, 0x00000000, 10)



    -- BLOCK 4: OUTPUTS AND NEURAL NETWORK VISUALISATION 

        -- Refresh Outputs
        for i = 1, 6 do
            controller["P1 " .. buttonNames[i]] = false
        end

        for i = 1, 6 do
            controller["P1 " .. buttonNames[i]] = outputsAbsolute[i] 
        end
        joypad.set(controller)

        -- Draw Buttons
        for i = 1, 6 do
            if outputs[i] == false then
                gui.drawText(220, 4 + 8*i, buttonNames[i], 0xff000000, 0x00000000, 10 )
                gui.drawBox(215, 8 + 8*i, 218, 11 + 8*i, 0xff888888, 0x40000000)  
            end
            if outputs[i] == true then
                gui.drawText(220, 4 + 8*i, buttonNames[i], 0xff276d1c, 0x00000000, 10 )
                gui.drawBox(215, 8 + 8*i, 218, 11 + 8*i, 0xffffffff, 0xffffffff)  
            end
        end

    --[[	
        for i = 1, 247, 1 do
            if i <= 240 then
                nodeX[i] = 4 + 4 * (i%16)
                nodeY[i] = 12 + 4 * (math.floor(i/16)-1)
            end
            if i == 241 then
                nodeX[i] = 16*4
                nodeY[i] = 79
            do
            if i >= 242 and i <= 247 then
                nodeX[i] = 215
                nodeY[i] = 8 + 8*(i-241)
            do
        end	

        for i = 1, 247, 1 do
            nodeDrawn[i] = true
        end

        for i = 248, #nodes do
            nodeDrawn[i] = false
        end

        for i = 247, #nodes do 	
            nodeNumber = nodes[i]
            if nodeDrawn[nodeNumber] == false then
                nodeX[nodeNumber] = 147 + math.floor((i-247)/8)*20	
                nodeY[nodeNumber] = 12 + ((i-247)%8)*10 
                nodeDrawn[nodeNumber] = true
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
        nodeOuput[241] = 1

        for i = 247, #nodes do
            nodeOutput[i] = 0
        end


        for i = 1, #connections do	
            source = connection[i][1] 
            sink = connection[i][2]
            weight = connection[i][3]

            if nodeOutput[source] == 1 then
                nodeOuput[sink] = 1
            end
            if nodeOutput[source] == 0 then
                nodeOuput[sink] = 0
            end
            if nodeOutput[source] == -1 then
                nodeOuput[sink] = -1
            end

            if nodeDrawn[source] and nodeDrawn[sink] then
                if nodeOutput[source] == 0 then 
                    if weight >= 0 then
                        gui.drawLine(nodeX[source]+1, nodeY[source]+1, nodeX[sink]+1, nodeY[sink]+1, 0x4F00ff00)
                    end
                    if weight < 0 then 
                        gui.drawLine(nodeX[source]+1, nodeY[source]+1, nodeX[sink]+1, nodeY[sink]+1, 0x4Fff0000)
                    end
                end
                else
                    if weight >= 0 then
                        gui.drawLine(nodeX[source]+1, nodeY[source]+1, nodeX[sink]+1, nodeY[sink]+1, 0xFF00ff00)
                    end
                    if weight < 0 then 
                        gui.drawLine(nodeX[source]+1, nodeY[source]+1, nodeX[sink]+1, nodeY[sink]+1, 0xFFff0000)
                    end
                end
            end	
        end

        for i = 248, #nodes do
            if nodeDrawn[i] == true then
                if nodeOuput[i] == 0 then
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

    --]]





        emu.frameadvance();
    end
end

