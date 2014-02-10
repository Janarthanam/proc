import sys
import utils
import xlrd
import glob
import logging
from audit_writer import AuditReportWriter

logging.basicConfig(level=logging.DEBUG)

ifiles = glob.glob(sys.argv[1])

for ifile in ifiles:
    logging.info("Processing file:" + ifile)
#print "The number of worksheet is: %d" % book.nsheets
    try:
        book = xlrd.open_workbook(ifile,encoding_override="cp1252")
        sheet = book.sheet_by_name("Findings & CAP")
    except xlrd.XLRDError as e:
        logging.exception("Unable to open -Findings & CAP- in file: " + ifile )
        continue

    ar = AuditReportWriter(ifile+'.xls','Findings & CAP')

    for rx in range(2,sheet.nrows):
        finding = sheet.cell_value(rowx=rx,colx=4) #Column E, row = rx
        #print finding;
        if finding.lower() == "n/a" or finding.strip() == '':
            continue

        findingdetail1 = sheet.cell_value(rowx=rx,colx=5) #Column F, row=rx
        findingdetail2 = sheet.cell_value(rowx=rx,colx=6) #Column G, row=rx
        id = sheet.cell_value(rowx=rx,colx=1) #Column A, row=rx

        try:
            findings = finding.strip().splitlines();  #strip all extra whitespaces and new lines

            d1 = findingdetail1.strip()  #remove leading whitespace
            d2 = findingdetail2.strip()  #remove leading whitespace

            if d1.lower() == 'n/a' or d1.strip() == '' : d1 = ''
            if d2.lower() == 'n/a'or d2.strip() == '' : d2 = ''
        except:
            logging.exception("Error reading, row: " + str(rx))
            #try to write row back
            ar.write_row(rx+1,id,finding,unicode(findingdetail1)+"\n" + unicode(findingdetail2),"Cond4: Neelansha Madam. Please look" + str(sys.exc_info()))
            logging.exception(unicode(findingdetail1)+"\n" + unicode(findingdetail2))
            continue
            

        (fhdr,numbered_findings) = utils.extract_numbered_entries("\n".join(findings))
        (fdhdr,numbered_finding_details) = utils.extract_numbered_entries(d1+'\n'+d2)
        
        #Check for numeric matches - code matched as Cond3
        if( numbered_findings and numbered_finding_details and len(numbered_findings) == len(numbered_finding_details)):
            for i in range(len(numbered_findings)):
                #print u"Row:%d:cond3 numeric:" % (rx) + numbered_findings[i] + "\t" + numbered_finding_details[i]
                ar.write_row(rx+1,id,fhdr + numbered_findings[i] ,fdhdr + numbered_finding_details[i],"Cond3: Numeric match")
        #Cond2 - two findings with d1 and d2
        elif not numbered_findings:
            #equality check for 2 - code named Cond2
            if len(findings) == 2 and d1 != '' and d2 != '':
                ar.write_row(rx+1,id,findings[0],d1,"Cond2")
                ar.write_row(rx+1,id,findings[1],d2,"Cond2")
            #one finding with d1 and optional d2 - code named Cond1
            elif len(findings) == 1:
                #print u"Row:%d:cond1:" % (rx) + findings[0] + "\t" + d1 + d2;
                ar.write_row(rx+1,id,findings[0],d1+d2,"Cond1")
            #Cond4 - unmatched findings and finding details after line split
            else:
                ar.write_row(rx+1,id,finding,(d1 + "\n" + d2),"Cond4: Neelansha Please look at it!")
        # Neelansha madam's special case - Cond2.1
        elif numbered_findings and (not numbered_finding_details or len(numbered_findings) != len(numbered_finding_details)):
            for finding in numbered_findings:
                ar.write_row(rx+1,id,finding,d1+'\n'+d2,"Cond2.1")
        else:
            #Cond4 - no such match. Dump findings and finding details and notify
            ar.write_row(rx+1,id,finding,(d1 + "\n" + d2),"Cond4: Neelansha Please look at it!")

    logging.info('Written file: ' + ifile + ".xls")    
    ar.save()
