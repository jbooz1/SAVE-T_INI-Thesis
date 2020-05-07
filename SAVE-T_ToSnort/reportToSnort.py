import logging
import argparse
import os
import json
import re


def parse_report_facts(report, prop):
    """
    Parse a SAVE-T Operation report for facts regarding a given fact property
    
    report: a string path to a report file
    prop: a string containing all or a portion of the fact property you are looking for
                If you are looking for remote vulnerabilities, then you can supply 'remote.vuln' or 
                to look for metasploit vulnerabilities, you can supply 'remote.vuln.metasploit'

    returns: a list of the fact values for vulnerabilites.
    """
    logger = logging.getLogger('program')
    logger.debug(f"Trying to parse {report} for vulnerability facts")

    with open(report, 'r') as file:
        j = json.load(file)
        count = 0
        fact_list = []
        for fact in j['facts']:
            if prop in fact['property']:
                logger.debug(f"Found fact type {fact['property']} with value {fact['value']}")
                fact_list.append(fact['value'])

        logger.debug(f"Found {len(fact_list)} related facts")
        return fact_list


def find_rules(fact_list):
    logger = logging.getLogger('program')
    logger.debug(f"Finding rules to match facts")

    rules_dict = {}
    match_rules = []

    # parse the rules taxonomy into a dictionary where the vulnerability type is the key
    with open("taxonomy.csv") as f:
        for line in f:
            (key, val) = line.split(',')
            rules_dict[key] = val

    # for each fact, see if there is a matching rule
    for fact in fact_list:
        split = fact.split(':')  # splits fact into pieces  IP_ADDRESS : PORT : VULN   for vuln facts

        # if there is a matching rule, replace the variables with the ip and port data
        if rules_dict[split[2]]:
            logger.debug(f"Found rules match for vuln {split[2]}")
            rule = re.sub('IPADDRESS', split[0], rules_dict[split[2]])
            rule = re.sub('PORT', split[1], rule)

            # append this new rule to the list of rules we need. 
            match_rules.append(rule)

    return match_rules

def main():

    # configure logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='./log/app.log',
                        filemode='w')
    logger = logging.getLogger('program')
    console = logging.StreamHandler()
    form = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(form)
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)

    # parse command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=str, required=True, help='path to the report you want to parse')
    parser.add_argument("--output", type=str, required=True, help='path to the file you want to output snort rules to')
    args = parser.parse_args()
    report_path = args.report

    # not a valid file, so exit
    if not os.path.isfile(report_path):
        print(f"Not a valid file: {report_path}")
        exit(1)

    ## valid file found

    # parse out the vulnerability facts
    vuln_list = parse_report_facts(report_path, 'remote.vuln')

    # clean up the fact strings that are found
    i = 0
    for v in vuln_list:
        vuln_list[i] = re.sub('http://', '', v)  # remove http:// from fact
        vuln_list[i] = re.sub('/(.*)/', '', vuln_list[i])  # remove the URI path from fact
        i += 1  


    match_rules = find_rules(vuln_list)

    # write rules to file
    logger.debug(f"Writing {len(match_rules)} snort rules to {args.output}")
    with open(args.output, 'w+') as out:
        for m in match_rules:
            out.write(m)

if __name__ == "__main__":
    main()
