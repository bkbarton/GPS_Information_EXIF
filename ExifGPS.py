#Author : Benjamin Barton
#Data   : 1/13/2016
#Purpose: Read EXIF data and retrieve GPS degree's
import struct
import sys
#should use better structure in the future:
TAGS = {
    0x8825: "GPSInfo"
    }
ASCII = 'c'
SHORT = 'h' 
LONG = 'I'
RATIONAL = 'Q'
GPSTAGS = {
    1: ("GPSLatitudeRef",ASCII),
    2: ("GPSLatitude",LONG),
    3: ("GPSLongitudeRef",ASCII),
    4: ("GPSLongitude",LONG)
}

#will get gps location from exif data
def get_gps_data(f):
    exif_data = []
    image_format = ''
    #skip reading number of entries, straight to reading tag of first entry
    #if we put counter to 8 we can read number of entries in IFD, which would determine how many loops are executed
    #size = struct.unpack('h',f.read(2))
    counter = 400 #was 10
    offset = counter
    count = 0
    #get byteorder
    order = struct.unpack('h',f.read(2))
    #II
    if order == 0x4949:
        image_format = '<'

    #MM    
    else:
        image_format = '>'
    f.seek(8)    
    size = struct.unpack('h',f.read(2))  
   ####search through file, retrieving gps tags###############
    found = False
    while (found == False):
#searching through IFD for entry with specific tag 
        offset = counter
        #make sure file pointer starts at 10
        f.seek(offset)
        header_tag = struct.unpack(((image_format+'H')),f.read(2))
        
      ###### GPS INFORMATION #######
        if header_tag[0] == 0x8825:
            i = 4
            jump = 1
            test = 1
            direction = ''
            f.read(6)
            gps_offset = (struct.unpack(((image_format+'I')),f.read(4)))
            counter = gps_offset[0] + 10
            f.seek(counter)
            while (i > 0):
                offset = counter
                f.seek(offset)
                test = jump
                i -= 1
                #data that is needed, still has several errors
                #need to unpack using different arguments, currently system dependent 
                if(test == 1):
                    #this print shows direction
                    direction =(struct.unpack(((image_format+'c')),f.read(1)))[0]
                    
                    jump = 4
                    counter += 12
                    #f.read(11)
                else:
                    #go to location in file where specific GPS data is held
                    ref = ((struct.unpack((image_format+'I'),f.read(4))))
                    f.seek(ref[0])
                    
                    

                    #DECIMAL
                    numerator = (struct.unpack((image_format + 'I'),f.read(4)))
                    denominator = (struct.unpack((image_format + 'I'),f.read(4)))
                    decimal = (numerator[0] / denominator[0])
                    

                    #MINUTES
                    numerator = (struct.unpack((image_format + 'I'),f.read(4)))
                    denominator = (struct.unpack((image_format + 'I'),f.read(4)))
                    minutes = (numerator[0] / denominator[0])
                   

                    #SECONDS
                    numerator = (struct.unpack((image_format + 'I'),f.read(4)))
                    denominator = (struct.unpack((image_format + 'I'),f.read(4)))
                    seconds = (numerator[0] / denominator[0])
                    

                    #Calculation
                    solution = (decimal + (minutes/60) + (seconds /3600))
                    if direction in (b'S' , b'W'):
                        solution = -solution
                        
                    exif_data.append(solution)
                    #switch back to jump 1
                    jump = 1
                    #increment counter/offset
                    counter += 12
            found = True
        else:
            counter += 12
            count+=1
            if(count == size):
                found = True
            
    return exif_data
	
def main():
    f = open(str(sys.argv[1]), 'rb')
    data = get_gps_data(f)
    print(data)
    f.close()


