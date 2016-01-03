
def read_to_memory(reader):
    fh = reader._fh
    textual_reel_header = reader._textual_reel_header
    binary_reel_header = reader._binary_reel_header
    extended_textual_headers = reader._extended_textual_headers
    trace_offset_catalog = reader._trace_offset_catalog
    trace_length_catalog = reader._trace_length_catalog
    trace_header_packer = reader._trace_header_packer
    encoding = reader._encoding
    endian = reader._endian
    revision = reader._revision
    bytes_per_sample = reader._bytes_per_sample
    data_sample_format = reader.data_sample_format
    trace_samples = [reader.trace_samples(x) for x in reader.trace_indexes()]
    trace_headers = [reader.trace_header(x) for x in reader.trace_indexes()]
    
    memdataset = MemDataset(fh, textual_reel_header, binary_reel_header, extended_textual_headers,
                            trace_offset_catalog, trace_length_catalog, trace_header_packer,
                            encoding, trace_samples, trace_headers, revision, bytes_per_sample,
                            data_sample_format, endian=endian)
    return memdataset

class MemDataset(object):
    """ This is an in-memory implementation of the segpy dataset """
    
    def __init__(self, fh,
                 textual_reel_header,
                 binary_reel_header,
                 extended_textual_headers,
                 trace_offset_catalog,
                 trace_length_catalog,
                 trace_header_packer,
                 encoding,
                 trace_samples,
                 trace_headers,
                 revision,
                 bytes_per_sample,
                 data_sample_format,
                 endian='>'):
        self._fh = fh
        self._endian = endian
        self._encoding = encoding

        self._textual_reel_header = textual_reel_header
        self._binary_reel_header = binary_reel_header
        self._extended_textual_headers = extended_textual_headers

        self._trace_header_packer = trace_header_packer

        self._trace_offset_catalog = trace_offset_catalog
        self._trace_length_catalog = trace_length_catalog
        self._trace_samples = trace_samples
        self._trace_headers = trace_headers
        
        self._data_sample_format = data_sample_format

        self._revision = revision
        self._bytes_per_sample = bytes_per_sample
        self._max_num_trace_samples = None

    @property
    def textual_reel_header(self):
        """The textual real header as an immutable sequence of forty Unicode strings each 80 characters long.
        """
        return self._textual_reel_header
        
    @property
    def binary_reel_header(self):
        """The binary reel header.
        """
        return self._binary_reel_header
    
    @property
    def extended_textual_header(self):
        """A sequence of sequences of Unicode strings. If there were no headers, the sequence will be empty.
        """
        return self._extended_textual_headers
    
    @property    
    def dimensionality(self):
        """The spatial dimensionality of the data: 3 for 3D seismic volumes, 2 for 2D seismic lines, 1 for a
        single trace_samples, otherwise 0.
        """
        return self._dimensionality()
           
    def _dimensionality(self):
        return 1 if self.num_traces() == 1 else 0
        
    @property
    def data_sample_format(self):
        """The data type of the samples in machine-readable form.

        Returns:
            One of the values from datatypes.DATA_SAMPLE_FORMAT
        """
        return self._data_sample_format
    
    def trace_indexes(self):
        """An iterator over zero-based trace_samples indexes.
        Returns:
            An iterator which yields integers in the range zero to
            num_traces() - 1
        """
        return self._trace_offset_catalog

    def trace_header(self, trace_index):
        """The trace header for a given trace index."""
        return self._trace_headers[trace_index]
        
    def trace_samples(self, trace_index):
        """The trace samples for a given trace index."""
        return self._trace_samples[trace_index]
