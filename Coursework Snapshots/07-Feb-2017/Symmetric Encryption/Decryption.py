original = "His palms are sweaty, knees weak arms are heavy. There's vomit on his sweater already, Mom's spaghetti. " \
           "He's nervous, but on the surface he looks calm and ready to drop bombs, but he keeps on forgetting. " \
           "What he wrote down, the whole crowd goes so loud. He opens his mouth but the words won't come outt. " \
           "He's choking, how? Everybody's joking now. The clock's run out, times up, over BLOW! "

for character in original:
    x = ord(character)
    result += chr(x + 5)
