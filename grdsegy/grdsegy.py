from grdsegy import memdataset
import array
from datetime import datetime

import segpy.binary_reel_header
import segpy.catalog
import segpy.packer
import segpy.writer
from segpy.trace_header import TraceHeaderRev1

import argparse

# TODO: Perhaps make the header less hard-coded
TEXTUAL_REEL_HEADER = \
('C 1 Instrument:grdsegy by Terra Australis Geophysica                            ',
 'C 2 Serial #:                                                                   ',
 'C 3 Manufacturer: Terra Australis Geophysica Pty Ltd                            ',
 'C 4 Recording format: SEGY (Rev 1)                                              ',
 'C 5 Sample format: MS-DOS IEE Floating Point; Little Endian; ASCII              ',
 'C 6 Gain Type: Fixed                                                            ',
 'C 7 DataBase File:                                                              ',
 'C 8 Reel #:                                                                     ',
 'C 9 Media Type:                                                                 ',
 'C10 Filters: Low cut: 3Hz   High cut: 825 Hz                                    ',
 'C11 Sample Interval: 500 us                Samples/Trace: 4001                  ',
 'C12 Trace/Record: 132                      Date:06-11-2015                      ',
 'C13 Traces Sorted By: Record               Line #:                              ',
 'C14 Record Length: 2000 ms                 CMP Fold: 1                          ',
 'C15 Client:                                Contractor:                          ',
 'C16 License #:                             Permit #:                            ',
 'C17 Project Name:                          Project #:                           ',
 'C18 Crew #:                                Headquarters:                        ',
 'C19 Area:                                  Manager:                             ',
 'C20 Observer(s):                                                                ',
 'C21 Proj Comments:                                                              ',
 'C22                                                                             ',
 'C23 Sensor Descr.:                                                              ',
 'C21 Man:          Model:         Type:         No:0  PatLen:0.00 Sep:0.0Freq:0  ',
 'C25                                                                             ',
 'C26                                                                             ',
 'C27                                                                             ',
 'C28 Source Descr. : None/Test                                                   ',
 'C29                                                                             ',
 'C30                                                                             ',
 'C31                                                                             ',
 'C32                                                                             ',
 'C33                                                                             ',
 'C34                                                                             ',
 'C35                                                                             ',
 'C36                                                                             ',
 'C37                                                                             ',
 'C38                                                                             ',
 'C39                                                                             ',
 'C40 END TEXTUAL HEADER                                                          ')
 
 

def read_grd(fh):
    """ Reads a grd file into a list """
    sig = fh.readline()
    if sig[:4] != 'DSAA':
        raise ValueError('Does not appear to be a grd file (no DSAA)')
    l = fh.readline()
    columns, rows = l.split()
    l = fh.readline()
    xmin, xmax = l.split()
    l = fh.readline()
    ymin, ymax = l.split()
    l = fh.readline()
    zmin, zmax = l.split()
    trace_samples = [array.array('d') for _ in range(0, int(columns))]
    for _ in range(0, int(rows)):
        l = fh.readline()
        i = 0
        for sample in l.split():
            trace_samples[i].append(float(sample))
            i += 1

    for sample in trace_samples:
        sample.reverse()
        
    sample_interval = (float(ymax) - float(ymin)) / (float(rows) - 1) * 1000
    return trace_samples, sample_interval, float(xmin), float(xmax)


def grd_to_memdataset(fh):
 
    trace_samples, sample_interval, xmin, xmax = read_grd(fh)
    textual_reel_header = TEXTUAL_REEL_HEADER
    binary_reel_header = segpy.binary_reel_header.BinaryReelHeader()
    binary_reel_header.data_traces_per_ensemble = len(trace_samples)
    binary_reel_header.auxiliary_traces_per_ensemble = 0
    binary_reel_header.sample_interval = int(sample_interval)  # milliseconds
    binary_reel_header.num_samples = len(trace_samples[0])  # samples per trace_samples
    binary_reel_header.data_sample_format = 5  # IEEE floating point
    binary_reel_header.ensemble_fold = 0
    binary_reel_header.trace_sorting = 1
    binary_reel_header.vertical_sum_code = 0
    binary_reel_header.sweep_frequency_at_end = 0
    binary_reel_header.sweep_frequency_at_start = 0
    binary_reel_header.sweep_length = 0
    binary_reel_header.sweep_type = 0
    binary_reel_header.sweep_trace_number = 0
    binary_reel_header.sweep_trace_length_at_end = 0
    binary_reel_header.sweep_trace_length_at_end = 0
    binary_reel_header.sweep_trace_length_at_start = 0
    binary_reel_header.taper_type = 0
    binary_reel_header.correlated_data_traces = 0
    binary_reel_header.binary_gain_recovered = 2
    binary_reel_header.amplitude_recovery_method = 0
    binary_reel_header.measurement_system = 1
    binary_reel_header.impulse_signal_polarity = 1
    binary_reel_header.vibratory_polarity_code = 0
    binary_reel_header.format_revision_num = 0
    binary_reel_header.fixed_length_trace_flag = 0
    binary_reel_header.num_extended_textual_headers = 0
    extended_textual_headers = []
    trace_offset_catalog = list(range(0, len(trace_samples)))
    trace_length_catalogue = segpy.catalog.RegularConstantCatalog(0,
        len(trace_samples), 1, len(trace_samples[0]))
    trace_header_packer = segpy.packer.HeaderPacker(TraceHeaderRev1)
    encoding = 'ascii'
    
    trace_headers = [TraceHeaderRev1() for _ in range(0, len(trace_samples))]
    th_count = 0
    for th in trace_headers:
        th.line_sequence_num = th_count + 1
        th.file_sequence_num = 0
        th.field_record_num = 1
        th.trace_num = th_count + 1
        th.energy_source_point_num = 0
        th.ensemble_num = th_count * 1000  # an incrementing number...? 
        th.ensemble_trace_num = len(trace_samples)

        th.trace_identification_code = 1
        th.num_vertically_summed_traces = 1
        th.num_horizontally_stacked_traces = 1
        th.data_use = 1
        
        th.source_receiver_offset = 0
        th.receiver_group_elevation = 0
        th.surface_elevation_at_source = 0
        th.source_depth_below_surface = 0
        th.datum_elevation_at_receiver_group = 0
        th.source_depth_below_surface = 0
        th.datum_elevation_at_source = 0
        th.water_depth_at_source = 0
        th.water_depth_at_group = 0
        th.elevation_scalar = 0
        th.xy_scalar = 0
        th.source_x = 0
        th.source_y = 0
        th.group_x = 0
        th.group_y = 0
        th.coordinate_units = 0

        th.weathering_velocity = 0
        th.subweathering_velocity = 0
        th.uphole_time_at_source = 0
        th.uphole_time_at_group = 0
        th.source_static_correction = 0
        th.group_static_correction = 0
        th.total_static = 0
        th.lag_time_a = 0
        th.lag_time_b = 0
        th.delay_recording_time = 0
        th.mute_start_time = 0
        th.mute_end_time = 0
        th.num_samples = len(trace_samples[0])
        th.sample_interval = sample_interval
        th.gain_type_of_field_instruments = 1
        th.instrument_gain_constant = 24
        th.instrument_initial_gain = 0
        th.correlated = 0
        th.sweep_frequency_at_start = 0
        th.sweep_frequency_at_end = 0
        th.sweep_length = 0
        th.sweep_type = 0
        th.sweep_trace_taper_length_at_start = 0
        th.sweep_trace_taper_length_at_end = 0
        th.taper_type = 0
        th.alias_filter_frequency = 0  # sample file had 825
        th.alias_filter_slope = 0  # sample file had 580
        th.notch_filter_frequency = 0

        th.notch_filter_slope = 0
        th.low_cut_frequency = 0
        th.high_cut_frequency = 0
        th.low_cut_slope = 0
        th.high_cut_slope = 0
        
        current_date = datetime.utcnow()
        
        th.year_recorded = current_date.year  # this was in the sample file
        th.day_of_year = current_date.day
        th.hour_of_day = current_date.hour
        th.minute_of_hour = current_date.minute
        th.second_of_minute = current_date.second
        th.time_basis_code = 2  # GMT
        th.trace_weighting_factor = 0
        th.geophone_group_num_roll_switch_position_one = 0
        th.geophone_group_num_first_trace_original_field = 0
        th.geophone_group_num_last_trace_original_field = len(trace_samples)
        th.gap_size = 0
        th.over_travel = 0
        
        th.cdp_x = 0
        th.cdp_y = 0
        
        th.inline_number = 0
        th.crossline_number = 0
        th.shotpoint_number = 0
        th.shotpoint_scalar = 0
        th.trace_unit = 0
        th.transduction_constant_mantissa = 327680  # it was in the sample file
        th.transduction_constant_exponent = 0
        th.transduction_units = 0

        th.device_trace_identifier = 0
        th.time_scalar = 0
        th.source_type = 0
        th.source_energy_direction = 0
        th.source_measurement_mantissa = 0
        th.source_measurement_exponent = 0
        th.source_measurement_unit = 0
        
        th_count += 1
    
    revision = 0
    bytes_per_sample = 4  # floating point - could be 8??
    data_sample_format = 'float32'
    
    mds = memdataset.MemDataset(fh,
                                textual_reel_header,
                                binary_reel_header,
                                extended_textual_headers,
                                trace_offset_catalog,
                                trace_length_catalogue,
                                trace_header_packer,
                                encoding,
                                trace_samples,
                                trace_headers,
                                revision,
                                bytes_per_sample,
                                data_sample_format,
                                endian='<')
                                
    return mds
    
def main():
    parser = argparse.ArgumentParser(description="Reads in a Surfer GRD file and creates a SEGY file with corresponding traces")
    parser.add_argument('-i', '--infile', dest='infile', required=True, help='Input GRD file name')
    parser.add_argument('-o', '--outfile', dest='outfile', required=True, help='Output filename (segy)')
    args = parser.parse_args()
    
    with open(args.infile) as ifh:
        mds = grd_to_memdataset(ifh)
    
    with open(args.outfile, 'wb') as ofh:
        segpy.writer.write_segy(ofh, mds)


if __name__ == '__main__':
    main()