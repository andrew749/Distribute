class Payload:

    def __init__(self, operation, data):
        self.payload_data = data
        self.payload_function = operation

    @staticmethod
    def _build_javascript_method(func, **kwargs):
        new_body = ""
        for x in kwargs.items():
            new_body += "var {variable_name} = {variable_data};\n".format(
                variable_name = x[0],
                variable_data = [a.encode('utf-8') for a in x[1]]
            )

        new_body += func
        return new_body

    def split_payload_data(self, number_of_nodes = 1):
        """
        Split payload data into slices

        yield:
            formatted exectuable payloads
        """
        payload_data_slices = []
        current_index = 0

        number_per_node = (len(self.payload_data)/number_of_nodes) + 1

        for x in xrange(number_of_nodes):
            payload_data_slices.append(self.payload_data[current_index: current_index + number_per_node])
            current_index += number_per_node

        for x in payload_data_slices:
            yield self._build_javascript_method(self.payload_function, payload_data = x)

    def to_dict(self):
        return  {
            'payload_operation': self.payload,
        }
