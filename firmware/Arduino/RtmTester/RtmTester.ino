/*
 * RTM Tester
 * Written by Jesus Vasquez
 * 10 August 2018
 *
 */
#include <Ethernet2.h>

// Firmware information strings
String FwName("RTM Tester");
String FwVer("v1.0.0");

// IO pins definition
int numOutputs = 32;
int outPins[] = { 17, 18, 19, 20, 21, 22, 23, 24, \
                  25, 26, 27, 28, 29, 30, 31, 32, \
                  33, 34, 35, 36, 37, 38, 39, 40, \
                  41, 42, 43, 44, 45, 46, 47, 48 };

int numInputs = 8;
int inPins[] = { 3, 5, 6, 8, 9, 14, 15, 16 };

// TCP Server configuration (listening on port 5000)
byte mac[] = {
    0x2C, 0xF7, 0xF1, 0x08, 0x1B, 0x0F
};
byte ip[] = {
    10, 0, 1, 100
};
IPAddress myDns(10, 0, 1, 1);
IPAddress gateway(10, 0, 1, 1);
IPAddress subnet(255, 0, 0, 0);
EthernetServer server(5000);

// Fw info string (static information is added here, and dynamic information is appended inside setup()
String FwInfo(
    FwName +                                              \
    "\nFW Version        : " + FwVer +                    \
    "\nNumber of inputs  : " + String(numInputs) +        \
    "\nNumber of outputs : " + String(numOutputs) +       \
    "\nMAC Address       : " + String(mac[0],HEX) + ":" + \
                               String(mac[1],HEX) + ":" + \
                               String(mac[2],HEX) + ":" + \
                               String(mac[3],HEX) + ":" + \
                               String(mac[4],HEX) + ":" + \
                               String(mac[5],HEX) +       \
    "\nIP Address        : "                              \
             ); // The IP address will be address inside setup(), after the Ethernet shield initialization

// Command string maximum length.
// Worse case scenario is command to write all outputs '=(2^numInputs-1)\n'
const int maxCmdSize = 20;

// Function to read the inputs channels
String readInputs()
{
    uint8_t v = 0;

    Serial.print("Reading inputs...\n");
    for (int i = 0; i < numInputs; i++)
    {
        if (digitalRead(inPins[i]) == HIGH)
            bitSet(v, i);
    }

    Serial.print("Done!\n");
    Serial.print("Value read was: 0x");
    Serial.print(v, HEX);
    Serial.print("\n");

    return String(v);
}

// Function to write the output channels
void writeOutputs(uint32_t v)
{
    Serial.print("Writing 0x");
    Serial.print(v, HEX);
    Serial.print(" to outputs...\n");

    for (int i = 0; i < numOutputs; i++)
        digitalWrite(outPins[i], bitRead(v, i));

    Serial.print("Done!\n");
}
void setup() {
    // initialize the Ethernet device
    Ethernet.begin(mac, ip, myDns, gateway, subnet);

    // start listening for clients
    server.begin();

    // Open serial communications and wait for port to open:
    Serial.begin(9600);
    while (!Serial) {
        ; // wait for serial port to connect. Needed for native USB port only
    }

    // Setup IO pins
    if (numInputs != sizeof(inPins)/sizeof(int))
        Serial.print("ERROR: numInputs and size of inPins array does not match!\n");

    for (int i = 0; i < numInputs; i++)
        pinMode(inPins[i], INPUT);

    if (numOutputs != sizeof(outPins)/sizeof(int))
        Serial.print("ERROR: numInputs and size of inPins array does not match!\n");

    for (int i = 0; i < numOutputs; i++)
        pinMode(outPins[i], OUTPUT);

    // Enable Fw info string, adding the dynamic information.
    // The static information was added during definition of the global variable.
    IPAddress realIP = Ethernet.localIP();
    FwInfo += String(realIP[0]) + ".";
    FwInfo += String(realIP[1]) + ".";
    FwInfo += String(realIP[2]) + ".";
    FwInfo += String(realIP[3]) + "\n";

    // Print FW information when booting
    Serial.print(FwInfo);
}

void sendString(EthernetClient c, String s)
{
    c.write(s.c_str());
}

void loop()
{
    EthernetClient client = server.available();

    // wait for a command from the client
    if (client)
    {
        // Replay:
        // The replay structure is:
        // [code]   [argument] [terminator]
        // [1 char]            [1 char]
        //
        // For invalid commands, the code will be '1' with empty argument. Otherwise it will be '0'.
        // For valid commands:
        // - For a Get inputs command the argument will be the value read from the digital pins (0-255 in ASCII).
        // - For a Set outputs command the argument will be empty.
        // - For a Get Fw info command the argument will be the Fw info string.
        //
        // The terminator will be '@'.
        String r       = "";    // String to hold the replay
        char   rCode   = '1';   // Replay code
        String rArg;            // Replay argument
        bool   rUseArg = false; // Does this replay contains an argument?


        // Process the command from the client:

        // Read how many bytes where sent
        int n = client.available();

        // Valid commands have length between 2 and maxCmdSize
        if( (n < 2) || (n > maxCmdSize))
        {
            Serial.print("Invalid command length. Omitting\n");

            // client.flush() doesn't clear the buffer,
            // So, let's clear the buffer manually.
            while (client.available())
                client.read();
        }
        else
        {
            // Print debug information
            Serial.print(n);
            Serial.print(" bytes received\n");

            // Extract the command and argument
            // The command structure is:
            // [type] . [argument]  [terminator]
            // [1 char] [0-3 chars] [1 char]
            //
            // Type of commands:
            // - Get inputs commands (cmd = '?'), no argument.
            // - Set outputs commands (cmd - '='), argument must be a numeric value between 0-255.
            // - Get FW info (cmd = 'i'), no argument.
            //
            // The terminator is '\n'.
            char     cmd       = client.read(); // Command
            String   cArg      = "";            // String to hold the command argument
            bool     cArgValid = true;          // Is the command argument valid?
            uint32_t cArgVal;                   // Numeric Argument value.

            // Read the argument.
            for (int i = 0; i < n-2; i++)
            {
                // Write each argument char in the argument string
                char c = static_cast<char>(client.read());
                cArg += c;

                // The argument can be only numeric, so it must only contain digits
                cArgValid &= isDigit(c);
            }

            // Discard the terminator character
            client.read();

            // If the command was Get and it contained an argument, it is invalid
            if ((cmd == '?' || cmd == 'i') && (n != 2))
                cArgValid = false;

            // Verify if the argument value is in the allowed range
            if (cArgValid)
                cArgVal = cArg.toInt();
                // As cArgVal is unsigned and its size is 32-bit, bigger numbers than 2^32-1 will be truncated,
                // so there is no way for testing if the value in in the range [0:2^32-1]

            // Print debug information
            Serial.print("Command = '");
            Serial.print(cmd);
            Serial.print("'\n");
            Serial.print("Argument = '");
            Serial.print(cArg);
            Serial.print("'\n");

            // Process only command with valid argument
            if (!cArgValid)
            {
                Serial.print("Command with invalid argument\n");
            }
            else
            {
                switch(cmd)
                {
                    case 'i':
                        rArg = FwInfo;
                        rUseArg = true;
                        rCode = '0';
                        break;
                    case '?':
                        rArg = readInputs();
                        rUseArg = true;
                        rCode = '0';
                        break;
                    case '=':
                        writeOutputs(cArgVal);
                        rCode = '0';
                        break;
                    default:
                        Serial.print("Unknown command\n");
                        break;
                }
            }
        }

        // Replay to client
        r += rCode;
        if (rUseArg)
        r += rArg;
        r += '@';

        sendString(client, r);

        // Print debug information
        Serial.print("Replay sent to client:\n");
        Serial.print(r);
        Serial.println("\n");
    }
}
