#!/usr/bin/env python

def get_real_ID(dummy_ID, shift_pattern):
    ''' Input a fake numeric ID, return its original numeric ID.
    
        :param dummy_ID: An input shifted numeric ID (a dummy ID).
        :type dummy_ID: str
        :param shift_pattern: A shift pattern to perform the reverse digit shifting.
        :type shift_pattern: str
        :returns: A real ID.
    '''
    if not (dummy_ID.isdigit() and shift_pattern.isdigit()):
        raise ValueError("One or both of dummy_ID and shift_pattern is/are not numeric")
        
    real_ID = list(dummy_ID);

    c = 0;
    for k in range(0, len(dummy_ID)): ## TODO 20180607 If len(dummy_ID) is longer than len(shift_pattern) the code will break.
        digit = int(dummy_ID[k])
        shift = int(shift_pattern[c])
        if digit < shift:
		    dummy = 10 + digit - shift;
        else:
		    dummy = digit - shift;
	    

        real_ID[k] = str(dummy);
        c += 1;
        if c > len(shift_pattern):
            c = 0;
    
    return "".join(real_ID)

def get_fake_ID(real_ID, shift_pattern):
    ''' Input a numeric ID, return a fake, shifted numeric ID.
    
        :param real_ID: An input numeric ID to be shifted (can be accession ID, study ID or patient ID).
        :type real_ID: str
        :param shift_pattern: A shift pattern to perform the digit shifting.
        :type shift_pattern: str
        :returns: A fake, shifted numeric ID.
    '''
    if not (real_ID.isdigit() and shift_pattern.isdigit()):
        raise ValueError("One or both of real_ID and shift_pattern is/are not numeric")

    dummy_ID = list(real_ID)

    c = 0;
    for k in range(0, len(real_ID)):
        digit = int(real_ID[k])
        shift = int(shift_pattern[c])
        dummy = digit + shift;
        if dummy >= 10:
            dummy = dummy - 10;
            
        dummy_ID[k] = str(dummy);
        c += 1;
        if c > len(shift_pattern):
            c = 0;
        
    return "".join(dummy_ID)
    
def main():
    ''' This main function is rarely used. '''
    import csv
    import sys
    
    input_csv = sys.argv[1]
    pattern = sys.argv[2]
    pattern = pattern.strip()
    with open(input_csv, 'rb') as f:
        for line in f:
            line = line.strip()
            try:
                real_id = get_real_ID(line, pattern)
                print line + ',' + real_id
            except:
                print sys.exc_info()[0]
                continue
                
            
if __name__ == '__main__': 
    ''' Rarely called as an executable '''
    main()

