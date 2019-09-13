#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>

typedef struct cfg {
  char *server;
  char *from_address;
  char *to_address;
  char *message;
} cfg_t;

/* 
 * Entry function for sending mail via SMTP.
 * The input argument is a configuration structure
 * with the necessary data to form an email message
 * and send it to a specific server.
*/
void send_mail(cfg_t *cfg) {
  printf("Arguments: %s %s %s %s\n", cfg->server,
	 cfg->from_address, cfg->to_address, cfg->message);
}

int main(int argc, char **argv) {
  int c;
  
  cfg_t cfg = {
    .server = NULL,
    .from_address = NULL,
    .to_address = NULL,
    .message = NULL
  };
  
  if (argc < 5) {
    fprintf(stderr,
	    "Usage: %s <server> <from> <to> <message>\n",
	    argv[0]);
    exit(1);
  }

  cfg.server = strdup(argv[1]);
  cfg.from_address = strdup(argv[2]);
  cfg.to_address = strdup(argv[3]);
  cfg.message = strdup(argv[4]);
  
  send_mail(&cfg);

  return 0;
}
