# -*- coding: utf-8 -*-
import pylspclient
import subprocess
import threading
import logging
import logging.config as log_config
import os
import yaml


# See more information on the project page: https://github.com/palantir/python-language-server

def setup_logging():
    path = "custom-logging.yml"
    if os.path.exists(path):
        config = yaml.safe_load(open(path))
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)


setup_logging()
logger = logging.getLogger(__name__)


def _gen_capabilities():
    return {
            'workspace': {
                'workspaceEdit': {
                    'documentChanges': True, 
                    'failureHandling': 'abort'
                }, 
                'inlayHint': {'refreshSupport': True}, 
                'semanticTokens': {'refreshSupport': True}, 
                'executeCommand': {}, 
                'configuration': True, 
                'applyEdit': True, 
                'workspaceFolders': True, 
                'symbol': {
                    'dynamicRegistration': True, 
                    'symbolKind': {
                        'valueSet': [2, 24, 18, 13, 4, 14, 23, 26, 3, 6, 19, 12, 5, 11, 20, 9, 15, 17, 8, 16, 21, 25, 1, 10, 22, 7]
                    }, 
                    'tagSupport': {'valueSet': [1]}
                }, 
                'didChangeConfiguration': {'dynamicRegistration': True}, 
                'codeLens': {'refreshSupport': True}
            }, 
            'general': {
                'regularExpressions': {'engine': 'ECMAScript'}, 
                'markdown': {
                    'parser': 'Python-Markdown', 
                    'version': '3.2.2'
                }
            }, 
            'textDocument': {
                'codeAction': {
                    'dataSupport': True, 
                    'dynamicRegistration': True, 
                    'isPreferredSupport': True, 
                    'resolveSupport': {'properties': ['edit']}, 
                    'codeActionLiteralSupport': {
                        'codeActionKind': {
                            'valueSet': ['quickfix', 'refactor', 'refactor.extract', 'refactor.inline', 'refactor.rewrite', 'source.fixAll', 'source.organizeImports']
                        }
                    }
                }, 
                'callHierarchy': {'dynamicRegistration': True}, 
                'inlayHint': {
                    'dynamicRegistration': True, 
                    'resolveSupport': {
                        'properties': ['textEdits', 'label.command']
                    }
                }, 
                'selectionRange': {'dynamicRegistration': True}, 
                'rangeFormatting': {'dynamicRegistration': True}, 
                'documentLink': {'dynamicRegistration': True, 'tooltipSupport': True}, 
                'rename': {'dynamicRegistration': True, 'prepareSupport': True, 'prepareSupportDefaultBehavior': 1}, 
                'colorProvider': {'dynamicRegistration': True}, 
                'typeDefinition': {'linkSupport': True, 'dynamicRegistration': True}, 
                'declaration': {'linkSupport': True, 'dynamicRegistration': True}, 
                'references': {'dynamicRegistration': True}, 
                'synchronization': {'dynamicRegistration': True, 'willSaveWaitUntil': True, 'didSave': True, 'willSave': True}, 
                'definition': {'linkSupport': True, 'dynamicRegistration': True}, 
                'semanticTokens': {
                    'overlappingTokenSupport': False, 
                    'dynamicRegistration': True, 
                    'tokenModifiers': ['abstract', 'modification', 'deprecated', 'defaultLibrary', 'readonly', 'static', 'documentation', 'async', 'declaration', 'definition'], 
                    'requests': {'range': True, 'full': {'delta': True}}, 
                    'augmentsSyntaxTokens': True, 
                    'formats': ['relative'], 
                    'tokenTypes': ['event', 'variable', 'keyword', 'struct', 'typeParameter', 'namespace', 'class', 'regexp', 'comment', 'decorator', 'interface', 'macro', 'string', 'type', 'parameter', 'method', 'function', 'property', 'operator', 'enum', 'number', 'enumMember', 'modifier'], 
                    'multilineTokenSupport': True
                }, 
                'implementation': {'linkSupport': True, 'dynamicRegistration': True}, 
                'signatureHelp': {
                    'dynamicRegistration': True, 
                    'contextSupport': True, 
                    'signatureInformation': {
                        'activeParameterSupport': True, 
                        'parameterInformation': {'labelOffsetSupport': True}, 
                        'documentationFormat': ['markdown', 'plaintext']
                    }
                }, 
                'formatting': {'dynamicRegistration': True}, 
                'typeHierarchy': {'dynamicRegistration': True}, 
                'completion': {
                    'dynamicRegistration': True, 
                    'insertTextMode': 2, 
                    'completionItemKind': {
                        'valueSet': [9, 23, 19, 24, 1, 14, 21, 22, 15, 6, 12, 7, 25, 18, 3, 11, 8, 4, 5, 2, 13, 16, 17, 20, 10]
                    }, 
                    'completionItem': {
                        'insertReplaceSupport': True, 
                        'resolveSupport': {
                            'properties': ['detail', 'documentation', 'additionalTextEdits']
                        }, 
                        'insertTextModeSupport': {'valueSet': [2]}, 
                        'labelDetailsSupport': True, 
                        'documentationFormat': ['markdown', 'plaintext'], 
                        'snippetSupport': True, 
                        'tagSupport': {'valueSet': [1]}, 
                        'deprecatedSupport': True
                    }
                }, 
                'publishDiagnostics': {
                    'dataSupport': True, 
                    'relatedInformation': True, 
                    'versionSupport': True, 
                    'codeDescriptionSupport': True, 
                    'tagSupport': {'valueSet': [1, 2]}
                }, 
                'codeLens': {'dynamicRegistration': True}, 
                'documentSymbol': {
                    'dynamicRegistration': True, 
                    'hierarchicalDocumentSymbolSupport': True, 
                    'symbolKind': {
                        'valueSet': [2, 24, 18, 13, 4, 14, 23, 26, 3, 6, 19, 12, 5, 11, 20, 9, 15, 17, 8, 16, 21, 25, 1, 10, 22, 7]
                    }, 
                    'tagSupport': {'valueSet': [1]}
                }, 
                'hover': {
                    'dynamicRegistration': True, 
                    'contentFormat': ['markdown', 'plaintext']
                }, 
                'documentHighlight': {'dynamicRegistration': True}
            }, 
            'window': {
                'workDoneProgress': True, 
                'showDocument': {'support': True}, 
                'showMessage': {
                    'messageActionItem': {'additionalPropertiesSupport': True}
                }
            }
        }


def referencesCallback(params):
   logger.info(f"==referencesCallback==referencesCallback:{params}")
   return params


def executeClientCommandCallback(params):
   logger.info(f"executeClientCommandCallback:{params}")
   return params
   


def diagnosticsCallback(params):
    # print("文件诊断: {}".format(params))
    #logger.info(f"======diagnosticsCallback params:{params}======")
    return None


def clientRegisterCapability(params):
    # logger.info(f"======clientRegisterCapability params:{params}======")
    return None


def logMessageCallback(params):
    #logger.info(f"======logMessageCallback params:{params}======")
    message = params.get("message", "")
    if message:
        # print(message)
        pass


def languageStatus(params):
    #logger.info(f"======languageStatus params:{params}======")
    #status = params.get("type")
    #return status == "Started"
    pass


def showMessageCallback(params):
    #logger.info(f"======showMessageCallback params:{params}======")
    message = params.get("message", "")
    if message:
        # print("DEBUG: {}".format(message))
        pass


def process_item(pylspclient, lsp_client, uri, languageId, version, file_path, line,character):
    text = open(file_path, "r", encoding="utf-8").read()
    lsp_client.didOpen(pylspclient.lsp_structs.TextDocumentItem(uri, languageId, version, text))

    print("find definition:")
    result = lsp_client.definition(pylspclient.lsp_structs.TextDocumentIdentifier(uri),
                                   pylspclient.lsp_structs.Position(line, character))
    for r in result:
        print({
            "uri": r.uri,
            "start": {
                "line": r.range.start.line,
                "char": r.range.start.character
            },
            "end": {
                "line": r.range.end.line,
                "char": r.range.end.character
            }
        })
    print("find references:")
    result = lsp_client.references(pylspclient.lsp_structs.TextDocumentIdentifier(uri),
                                   pylspclient.lsp_structs.Position(line, character))
    print("result:", result)
    for r in result:
        print({
            "uri": r.uri,
            "start": {
                "line": r.range.start.line,
                "char": r.range.start.character
            },
            "end": {
                "line": r.range.end.line,
                "char": r.range.end.character
            }
        })


class ReadPipe(threading.Thread):

    def __init__(self, pipe):
        threading.Thread.__init__(self)
        self.pipe = pipe

    def run(self):
        #logger.info(f"=======ReadPipe run self.pipe:{self.pipe}======")
        line = self.pipe.readline().decode('utf-8')
        while line:
            print(line)
            line = self.pipe.readline().decode('utf-8')


if __name__ == "__main__":
    p = subprocess.Popen("""clangd""",
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    read_pipe = ReadPipe(p.stderr)
    read_pipe.start()
    json_rpc_endpoint = pylspclient.JsonRpcEndpoint(p.stdin, p.stdout)
    method_callbacks = {
        "client/registerCapability": clientRegisterCapability, # lambda _: None,
        "textDocument/references": referencesCallback,
        "workspace/executeClientCommand": executeClientCommandCallback
    }
    notify_callbacks = {
        "window/logMessage": logMessageCallback,
        "window/showMessage": showMessageCallback,
        "textDocument/publishDiagnostics": diagnosticsCallback,
        "language/status": languageStatus,
        "$/progress": languageStatus
    }
    # To work with socket: sock_fd = sock.makefile()
    lsp_endpoint = pylspclient.LspEndpoint(json_rpc_endpoint,
                                           method_callbacks=method_callbacks,
                                           notify_callbacks=notify_callbacks,timeout=600)
    lsp_endpoint.daemon = True
    lsp_client = pylspclient.LspClient(lsp_endpoint)
    capabilities = _gen_capabilities()
    # 指定工作目录
    root_uri = 'file:///security/fdisk1/projects/TarsCpp'

    workspace_folders = [{'name': 'TarsCpp', 'uri': root_uri}]

    # 指定待检查文件
    file_path = "/security/fdisk1/projects/TarsCpp/servant/promise/exception.h"

    uri = "file://" + file_path
    line = 81
    character = 23
    lsp_client.initialize(p.pid, None, root_uri, None, capabilities,
                          "messages", workspace_folders)
    lsp_client.initialized()

    languageId = pylspclient.lsp_structs.LANGUAGE_IDENTIFIER.JAVA
    version = 0
    process_item(pylspclient, lsp_client, uri, languageId, version, file_path, line, character)
    
    lsp_client.shutdown()
    lsp_client.exit()
    print("退出")
