#!/usr/bin/env python


import datetime


class ComtradeWriter:
    """
    A python Class to write IEEE Comtrade files.

    Based upon IEC 60255-24 Edition 2.0 2013-04, IEEE Std C37.111

    TODO: Currently only supports ASCII data files. Add support for binary files later

    """


    def __init__(self, filename, start, trigger, station_name="STN", rec_dev_id="", rev_year="1999",
                 lf=50, timemult=1.0):

        self.clear()

        self.filename = filename
        self.station_name = station_name
        self.rec_dev_id = rec_dev_id
        if rev_year not in ['1991', '1999', '2013']:
            raise ValueError('Invalid rev_year used to create writer')
        self.rev_year = rev_year
        self.lf = lf
        self.start = start
        self.trigger = trigger
        self.timemult = timemult

        datafilename = self.filename[0:-4] + '.dat'

        self.data_file_handler = open(datafilename, 'w')

    def clear(self):
        self.filename = ''
        self.config_file_handler = 0
        self.data_file_handler = 0

        self.station_name = ''
        self.rec_dev_id = ''
        self.rev_year = 1999

        self.TT = 0
        self.A = 0
        self.D = 0

        self.An = []
        self.Ach_id = []
        self.Aph = []
        self.Accbm = []
        self.uu = []
        self.a = []
        self.b = []
        self.skew = []
        self.min = []
        self.max = []
        self.primary = []
        self.secondary = []
        self.PS = []
        # Digital channel information:
        self.Dn = []
        self.Dch_id = []
        self.Dph = []
        self.Dccbm = []
        self.y = []
        self.lf = 0
        self.nrates = 0
        self.samp = []
        self.endsamp = []
        # Date/time stamps:
        #    defined by: [dd,mm,yyyy,hh,mm,ss.ssssss]
        self.start = "01/01/2000,00:00:00.000000"
        self.trigger = "01/01/2000,00:00:00.000000"
        # Data file type: we are locking this into ASCII for the moment
        self.ft = 'ASCII'
        # Time stamp multiplication factor:
        self.timemult = 1.0
        self.DatFileContent = ''

        # header data for .HDR file. No file is written if header equals None
        self.header = None

        # the number of the next sample in the data file
        self.next_sample_number = 1

    def finalize(self):
        """closes the writer by writing out and/or closing all of the remaining files"""
        self.__writeCFGFile(self.filename)
        if self.data_file_handler:
            self.data_file_handler.write("\x1A")
            self.data_file_handler.close()

        if self.header:
            headerfilename = self.filename[0:-4] + '.hdr'

            headerfilehandler = open(headerfilename, 'w')
            headerfilehandler.write(self.header)
            headerfilehandler.close()

        return

    def set_header_content(self, content):
        """Sets the optional header content that gets written into the .HDR file"""
        self.header = content

    def add_analog_channel(self, id: str, ph: str, ccbm: str, uu: str = "", a=1.0, b=0.0, skew=0.0, min=0.0, max=0.0,
                           primary=1.0, secondary=1.0, PS="P"):
        """adds an analog channel. All channels should be added before any data is added"""
        if PS not in ['p', 'P', 's', 'S']:
            raise ValueError('Invalid PS value used to add analog channel. Only valid values are p, P, s, S')

        self.A += 1
        self.TT += 1
        self.An.append(self.A)
        self.Ach_id.append(id)
        self.Aph.append(ph)
        self.Accbm.append(ccbm)
        self.uu.append(uu)
        self.a.append(a)
        self.b.append(b)
        self.skew.append(skew)
        self.min.append(min)
        self.max.append(max)
        self.primary.append(primary)
        self.secondary.append(secondary)
        self.PS.append(PS)
        return self.A

    def add_digital_channel(self, id, ph, ccbm, y):
        """adds a digital channel. All channels should be added before any data is added"""
        self.D += 1
        self.TT += 1
        self.Dn.append(self.D)
        self.Dch_id.append(id)
        self.Dph.append(ph)
        self.Dccbm.append(ccbm)
        self.y.append(y)
        return self.D

    def add_sample_record(self, offset, analog_data, digital_data):
        """adds a record for a particular offset from the start time stamp. The number of analog and digital
        data samples should match the number of analog and digital (respectively) channels already created.
        Failure to do so, will result in exceptions"""
        self.data_file_handler.write(str(self.next_sample_number)
                                     + ", "
                                     + str(offset)
                                     + ", "
                                     + ", ".join(analog_data)
                                     + ", "
                                     + ", ".join(digital_data)
                                     + "\r\n")

        self.next_sample_number += 1

    def __get_formatted_comtrade_ts(self, ts):
        """Given a time stamp, returns a formatted string in the format 01/01/2000,00:00:00.000000"""
        return ts.strftime('%d/%m/%Y,%H:%M:%S') + ('.%06d' % ts.microsecond)

    def __writeCFGFile(self, write_filename):
        """
        Writes the Comtrade header file (.cfg).
        """

        self.config_file_handler = open(write_filename, 'w')

        # write first line:
        self.config_file_handler.write(",".join((self.station_name, str(self.rec_dev_id), str(self.rev_year))) + "\r\n")

        # write second line:
        self.config_file_handler.write(",".join((str(self.TT), str(self.A) + "A", str(self.D) + "D")) + "\r\n")

        # writing analog channel lines:
        for i in range(self.A):
            self.config_file_handler.write(",".join((str(self.An[i]),
                                                     str(self.Ach_id[i]),
                                                     str(self.Aph[i]),
                                                     str(self.Accbm[i]),
                                                     str(self.uu[i]),
                                                     str(self.a[i]),
                                                     str(self.b[i]),
                                                     str(self.skew[i]),
                                                     str(self.min[i]),
                                                     str(self.max[i]),
                                                     str(self.primary[i]),
                                                     str(self.secondary[i]),
                                                     str(self.PS[i]))) + "\r\n")

        # writing digital channel lines:
        for i in range(self.D):
            self.config_file_handler.write(",".join((str(self.Dn[i]),
                                                     str(self.Dch_id[i]),
                                                     str(self.Dph[i]),
                                                     str(self.Dccbm[i]),
                                                     str(self.y[i]))) + "\r\n")

        # write line frequency:
        self.config_file_handler.write(str(self.lf) + "\r\n")

        # Read sampling rates:
        self.config_file_handler.write(str(self.nrates) + "\r\n")

        if (self.nrates==0):
            self.config_file_handler.write("0,"+  str(self.next_sample_number -1)+ "\r\n")
        else:
            for i in range(self.nrates):  # @UnusedVariable
                self.config_file_handler.write(",".join((str(self.samp[i]),
                                                         str(self.endsamp[i])
                                                         )) + "\r\n")

        # write start date and time ([dd,mm,yyyy,hh,mm,ss.ssssss]):
        self.config_file_handler.write(self.__get_formatted_comtrade_ts(self.start) + "\r\n")

        # write trigger date and time ([dd,mm,yyyy,hh,mm,ss.ssssss]):
        self.config_file_handler.write(self.__get_formatted_comtrade_ts(self.trigger) + "\r\n")

        # Write file type:
        self.config_file_handler.write(self.ft + "\r\n")

        # Write time multiplication factor:
        self.config_file_handler.write(str(int(self.timemult)) + "\r\n")

        # END READING .CFG FILE.
        self.config_file_handler.close()  # Close file.


