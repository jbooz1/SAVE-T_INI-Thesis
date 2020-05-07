The reportToSnort.py script will parse a SAVE-T operation report and output snort files to the specified file.

To use the script, supply a SAVE-T operation report with the `--report` flag and an output file location with the `--output` flag. 

The script uses a taxonomy of SAVE-T found vulnerabilities to snort rules which are used to block the attack for that vulnerability. This taxonomy is found in taxonomy.csv. The format here is to include the SAVE-T fact property first and the snort rule second with a comma (',') delimiter between them. 

The operation report parser assumes the following SAVE-T fact structure: `IP_ADDRESS:PORT:VULN_TYPE`. VULN_TYPE is currently ignored as the fact properties support here already indicate the type of vulnerability that was found. Extra parts of the fact string (e.g., URL pieces) are stripped by the parser. 