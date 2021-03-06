import logging
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.ProcessParser import ProcessParser
from utils import DotDict

LOG = logging.getLogger(__name__)
__author__ = 'Evren Esat Ozkan'




class CamundaBMPNParser(BpmnParser):
    def __init__(self):
        super(CamundaBMPNParser, self).__init__()
        self.PROCESS_PARSER_CLASS = CamundaProcessParser



# noinspection PyBroadException
class CamundaProcessParser(ProcessParser):
    def parse_node(self, node):
        """
        overrides ProcessParser.parse_node
        parses and attaches the inputOutput tags that created by Camunda Modeller
        :param node: xml task node
        :return: TaskSpec
        """
        spec = super(CamundaProcessParser, self).parse_node(node)
        spec.data = DotDict()
        try:
            input_nodes = self._get_input_nodes(node)
            if input_nodes:
                for nod in input_nodes:
                    spec.data.update(self._parse_input_node(nod))
        except Exception as e:
            LOG.exception("Error while processing node: %s" % node)
        spec.defines = spec.data
        # spec.ext = self._attach_properties(node, spec)
        return spec

    # def _attach_properties(self, spec, node):
    #     """
    #     attachs extension properties to the spec.ext object
    #     :param spec: task spec
    #     :param node: xml task node
    #     :return: task spec
    #     """
    #     return spec

    @staticmethod
    def _get_input_nodes(node):
        for child in node.getchildren():
            if child.tag.endswith("extensionElements"):
                for gchild in child.getchildren():
                    if gchild.tag.endswith("inputOutput"):
                        children = gchild.getchildren()
                        return children

    @classmethod
    def _parse_input_node(cls, node):
        """
        :param node: xml node
        :return: dict
        """
        data = {}
        child = node.getchildren()
        if not child and node.get('name'):
            val = node.text
        elif child:  # if tag = "{http://activiti.org/bpmn}script" then data_typ = 'script'
            data_typ = child[0].tag.split('}')[1]
            val = getattr(cls, '_parse_%s' % data_typ)(child[0])
        data[node.get('name')] = val
        return data

    @classmethod
    def _parse_map(cls, elm):
        return dict([(item.get('key'), item.text) for item in elm.getchildren()])

    @classmethod
    def _parse_list(cls, elm):
        return [item.text for item in elm.getchildren()]

    @classmethod
    def _parse_script(cls, elm):
        return elm.get('scriptFormat'), elm.text


