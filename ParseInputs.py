from bs4 import BeautifulSoup as bs


def get_page_dimension(content):

    # Get the width of the xml document to be used for finding
    # the center of the page
    dimensions = content.find('page')
    width = int(dimensions.get('width'))

    return width

def find_start_margin(results, nums):

    left_margins = []
    nums_margins = []

    # Store all of the left positions of the numbers in the margins,
    # then sort to get the left-most items
    for r in results:
        if str(r.string) in nums:
            left_align = r.get('l')
            nums_margins.append(int(left_align))

    nums_margins.sort()

    # Here I assume that there are at least 8 numbers,
    # slice the list to end up with something of a median range to be able to
    # use for the calculations, in case there are other lines in the document
    # that only include these numbers that are not the numbers in the left margins
    checker = nums_margins[2:8]

    # Take the average of the values in the sliced list to be the approximate average
    # left position of the numbers in the margins
    margin_checker = sum(checker) / len(checker)
    print(margin_checker)

    # If the current line is not a number and is not empty, then get the left position
    # of the line and store it in a list if it is greater than the calculated approximate
    # average left position of the numbers in the margins
    for r in results:
        if str(r.string) not in nums and r.string is not None:            
            left_align = int(r.get('l'))
            if left_align > margin_checker:
                left_margins.append(int(left_align))
        elif r.string is None:
            print("found none")
    print(left_margins)

    # Sort the left_margins, then take the first 10 lines and find the average to get an approximate
    # position of the average left position of the text we care about
    left_margins.sort()
    avg_start_margin = sum(left_margins[:10]) / 10

    print(avg_start_margin)

    return avg_start_margin

def clean_lines(lines):

    # Join together the lines into something cohesive
    joined = " ".join(lines)
        
    plaintiff = ""
    defendant = ""

    got_plaintiff = False

    # Split the joined lines at spaces to search for specific words
    words = joined.split(' ')

    # Search through all of the words collected and search for 'v.' or 'vs.',
    # and mark when the versus is found -- everything before is the plaintiff(s)
    # and everything after is the defendant(s)
    for word in words:
        if "v." in word.casefold() or "vs." in word.casefold():
            got_plaintiff = True
        else:
            if got_plaintiff:
                defendant += word + ' '
            else:
                plaintiff += word + ' '

    # Some form of the word "Plaintiff" may have been included at the end of the plaintiff
    # section, which is redundant, so remove the final word if it is
    plaintiff_words = plaintiff.split(' ')
    if 'plaintiff' in plaintiff_words[-1].casefold():
        plaintiff_words = plaintiff_words[:-1]
    plaintiff = " ".join(plaintiff_words)

    # Strip any leading and trailing whitespace from the plaintiff and defendant
    plaintiff = plaintiff.strip()
    defendant = defendant.strip()

    return plaintiff, defendant

def process_content(filename):
    
    """
    Steps:
    1) Go through and find the left indent so you only read values to the right of the numbered left margin
    2) Go through and find the first text that is centered, start reading in the first line after that
    **** At this point, only search for text that has a left_alignment the is the most near
    **** to the right of the numbered margins
    3) Stop once you get to the first instances of "defendant"
    4) Else, split at first instance of 'v.' or 'vs.'
        - everything before the versus is plaintiff, everything after is defendant(s)
    """

    content = []
    
    with open(filename, "r") as file:
        
        content = file.readlines()
        content = "".join(content)
        bs_content = bs(content, "lxml")

        # Search through the xml file for the 'line' tag
        results = bs_content.find_all('line')
        

        width = get_page_dimension(bs_content)

        # The text isn't always perfectly aligned, so choose an arbitrary
        # tolerance for determining if the line is in different location will help,
        # and the documents can be varying in dimension so we have to remain adaptable
        TOLERANCE = width / 20  
        
        # The sides of the given complaints are numbered, and we need to draw a distinction
        # between the desired text and the numbered text, i.e. we can't just scrape the left-most
        # aligned text in the document
        nums = [str(i) for i in range(30)]
        
        # This is approximately where the left aligned text we care about is
        avg_start_margin = find_start_margin(results, nums)


        """
        I made a few assumptions about what other documents might look like based on
        the provided examples:
        1) There would be some sort of left aligned headers with contact information
        2) Below the headers, there would be a title for where the complaint is being addressed
            - The title would always be below the headers, not in-line or above, and the titles
              are approximately justified to the center
        3) The Plaintiff(s) would always be followed by the word "Plaintiff" of some variation,
           The Defendant(s) would always be followed by the word "Defendant" of some variation,
           and the Plaintiff(s) and Defendant(s) would always be separated by some form
           of "v." or "vs."
        """

        found_headers = False
        found_title = False
        started_collecting = False
        done = False

        # The lines list holds all of the lines we care about
        lines = []

        # I use the baseline element of the line to make sure that the title is below the
        # contact information headers
        headers_baseline = -1

        # Now search line by line...
        for r in results:
            
            if done:
                print("done")
                break

            # I had some issues during testing when I didn't explicitly cast
            # the r.string to a string when I tried to index through said string,
            # so I explicitly casted it to a string anytime I did a comparison, just to be safe
            if str(r.string) not in nums and r.string is not None:
                
                left_align = int(r.get('l'))
                
                # If the left alignment of the line is about where we expect the 
                # left aligned text that we care about is located...
                if left_align + TOLERANCE >= avg_start_margin and left_align - TOLERANCE <= avg_start_margin:
                    
                    # First we find the contact headers and save the baseline location
                    if not found_headers:
                        found_headers = True
                        headers_baseline = int(r.get('baseline'))

                    # If we still haven't found the title yet, then we keep
                    # saving the header baseline location
                    elif found_headers and not found_title:
                        headers_baseline = int(r.get('baseline'))

                    # If we have found both the headers and the title, then we can
                    # begin collecting the left aligned text
                    elif found_headers and found_title:
                        
                        started_collecting = True

                        # The first time we see the word defendant, we are done collecting
                        if "defendant" in str(r.string).casefold():
                            done = True
                            continue

                        # Otherwise, we continue adding the current line to the lines list
                        else:
                            lines.append(str(r.string))
                else:

                    # We assume headers should be the first text to search for, if we haven't found
                    # it yet, then keep searching
                    if not found_headers:
                        continue

                    # Otherwise, we may have found our title
                    else:
                        right_edge = int(r.get('r'))
                        left_edge = int(r.get('l'))
                        baseline = int(r.get('baseline'))
                        dif = right_edge - left_edge
                        centr = left_edge + dif / 2

                        # The approximate center of the line was calculated to be
                        # the left edge of the line plus half the distance between the left and
                        # right edges of the line, and the center of the page ought to be
                        # half the width of the page
                        #
                        # If the calculated center is within 2 * TOLERANCE, and the baseline of
                        # the possible title is below the lowest baseline from the headers, then we
                        # consider the line to be a title line
                        if abs((width / 2) - centr) <= TOLERANCE * 2 and baseline > headers_baseline:
                            found_title = True
                            print(r.string)

                    # The plaintiff, defendant, and vs. lines are not necessarily left justified,
                    # but they are still generally further left than the title lines,
                    # so we check the line to see if it contains any of those values, and if so we
                    # add them to the list of lines we care about
                    if started_collecting:
                        if "defendant" in str(r.string).casefold():
                            done = True
                            continue
                        elif "v." in str(r.string).casefold() or "vs." in str(r.string).casefold():
                            lines.append(str(r.string))
                        
    
        # Now we clean the lines to find the plaintiff(s) and defendant(s),
        # which are returned by the clean_lines function

        return clean_lines(lines)
