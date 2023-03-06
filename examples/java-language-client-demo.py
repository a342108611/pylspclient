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
    #document = {
    #  "uri": uri
    #}
    #position = dict(line=222,character=28)
    result = lsp_client.references(pylspclient.lsp_structs.TextDocumentIdentifier(uri),
                                   pylspclient.lsp_structs.Position(line, character))
    #result = lsp_client.references(document, position)
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
    java_cmd = """
    java \
     -Dfile.encoding=UTF-8 \
     -Declipse.application=org.eclipse.jdt.ls.core.id1 \
     -Dosgi.bundles.defaultStartLevel=4 \
     -Declipse.product=org.eclipse.jdt.ls.core.product \
     -Dlog.level=ALL \
     -noverify \
     -Xmx1G \
     -Xms100m \
     -XX:+UseParallelGC \
     -XX:GCTimeRatio=4 \
     -XX:AdaptiveSizePolicyWeight=90 \
     -Dsun.zip.disableMemoryMapping=true \
     --add-modules=ALL-SYSTEM \
     --add-opens java.base/java.util=ALL-UNNAMED \
     --add-opens java.base/java.lang=ALL-UNNAMED \
     --add-opens java.base/sun.nio.fs=ALL-UNNAMED \
     -jar /install-package/jdt-language-server/plugins/org.eclipse.equinox.launcher_1.6.400.v20210924-0641.jar \
     -configuration /install-package/jdt-language-server/config_linux \
     -data /install-package/jdt-language-server/.data
    """
    p = subprocess.Popen(java_cmd,
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
    capabilities = {
      'general': {
        'markdown': {'parser': 'Python-Markdown', 'version': '3.2.2'},
        'regularExpressions': {'engine': 'ECMAScript'}
      },
      'workspace': {
        'codeLens': {'refreshSupport': True},
        'workspaceFolders': True,
        'didChangeConfiguration': {'dynamicRegistration': True},
        'inlayHint': {'refreshSupport': True},
        'workspaceEdit': {
          'documentChanges': True,
          'failureHandling': 'abort'
        },
        'semanticTokens': {'refreshSupport': True},
        'configuration': True,
        'executeCommand': {},
        'applyEdit': True,
        'symbol': {
          'dynamicRegistration': True,
          'tagSupport': {'valueSet': [1]},
          'symbolKind': {
            'valueSet': [12, 10, 16, 3, 19, 4, 23, 14, 26, 2, 24, 13, 18, 1, 22, 7, 21, 25, 9, 20, 15, 17, 8, 5, 6, 11]
          }
        }
      },
      'textDocument': {
        'codeLens': {
          'dynamicRegistration': True
        },
        'references': {'dynamicRegistration': True},
        'synchronization': {
          'dynamicRegistration': True,
          'willSave': True,
          'willSaveWaitUntil': True,
          'didSave': True
        },
        'documentSymbol': {
          'dynamicRegistration': True,
          'tagSupport': {'valueSet': [1]},
          'hierarchicalDocumentSymbolSupport': True,
          'symbolKind': {
            'valueSet': [12, 10, 16, 3, 19, 4, 23, 14, 26, 2, 24, 13, 18, 1, 22, 7, 21, 25, 9, 20, 15, 17, 8, 5, 6, 11]
          }
        },
        'colorProvider': {'dynamicRegistration': True},
        'typeDefinition': {'dynamicRegistration': True, 'linkSupport': True},
        'selectionRange': {'dynamicRegistration': True},
        'codeAction': {
          'dynamicRegistration': True,
          'codeActionLiteralSupport': {
            'codeActionKind': {
              'valueSet': ['quickfix', 'refactor', 'refactor.extract', 'refactor.inline', 'refactor.rewrite', 'source.fixAll', 'source.organizeImports']
            }
          },
          'resolveSupport': {'properties': ['edit']},
          'isPreferredSupport': True,
          'dataSupport': True
        },
        'rangeFormatting': {'dynamicRegistration': True},
        'typeHierarchy': {'dynamicRegistration': True},
        'documentLink': {'dynamicRegistration': True, 'tooltipSupport': True},
        'rename': {'dynamicRegistration': True, 'prepareSupport': True, 'prepareSupportDefaultBehavior': 1},
        'inlayHint': {
          'dynamicRegistration': True,
          'resolveSupport': {'properties': ['textEdits', 'label.command']}
        },
        'callHierarchy': {'dynamicRegistration': True},
        'declaration': {'dynamicRegistration': True, 'linkSupport': True},
        'hover': {'dynamicRegistration': True, 'contentFormat': ['markdown', 'plaintext']},
        'definition': {'dynamicRegistration': True, 'linkSupport': True},
        'completion': {
          'dynamicRegistration': True,
          'completionItemKind': {
            'valueSet': [18, 3, 12, 2, 15, 14, 22, 21, 25, 9, 23, 16, 19, 1, 17, 20, 10, 6, 4, 13, 24, 5, 11, 7, 8]
          },
          'insertTextMode': 2,
          'completionItem': {
            'tagSupport': {'valueSet': [1]},
            'snippetSupport': True,
            'deprecatedSupport': True,
            'resolveSupport': {
              'properties': ['detail', 'documentation', 'additionalTextEdits']
            },
            'insertReplaceSupport': True,
            'insertTextModeSupport': {'valueSet': [2]},
            'labelDetailsSupport': True,
            'documentationFormat': ['markdown', 'plaintext']
          }
        },
        'documentHighlight': {'dynamicRegistration': True},
        'publishDiagnostics': {
          'relatedInformation': True,
          'tagSupport': {'valueSet': [1, 2]},
          'versionSupport': True,
          'codeDescriptionSupport': True,
          'dataSupport': True
        },
        'formatting': {'dynamicRegistration': True},
        'signatureHelp': {
          'dynamicRegistration': True,
          'contextSupport': True,
          'signatureInformation': {
            'activeParameterSupport': True,
            'parameterInformation': {'labelOffsetSupport': True},
            'documentationFormat': ['markdown', 'plaintext']
          }
        },
        'semanticTokens': {
          'formats': ['relative'],
          'augmentsSyntaxTokens': True,
          'tokenTypes': ['namespace', 'function', 'modifier', 'method', 'type', 'regexp', 'keyword', 'struct', 'typeParameter', 'event', 'variable', 'enumMember', 'parameter', 'property', 'operator', 'enum', 'string', 'comment', 'decorator', 'class', 'number', 'macro', 'interface'],
          'dynamicRegistration': True,
          'overlappingTokenSupport': False,
          'tokenModifiers': ['declaration', 'definition', 'documentation', 'async', 'defaultLibrary', 'static', 'readonly', 'modification', 'abstract', 'deprecated'],
          'multilineTokenSupport': True,
          'requests': {
            'full': {'delta': True},
            'range': True
          }
        },
        'implementation': {'dynamicRegistration': True, 'linkSupport': True}
      },
      'window': {
        'workDoneProgress': True,
        'showDocument': {'support': True},
        'showMessage': {
          'messageActionItem': {'additionalPropertiesSupport': True}
        }
      }
    }
    # 指定工作目录
    root_uri = 'file:///install-package/RuoYi-Vue'
    #root_uri = "file:///security/fdisk1/projects/JSH_ERP/jshERP-boot"
    # root_path = '/install-package/RuoYi-Vue'
    #root_path = "/security/fdisk1/projects/JSH_ERP/jshERP-boot"
    workspace_folders = [{'name': 'RuoYi-Vue', 'uri': root_uri}]
    #workspace_folders = [{'uri':root_uri}]
    # 指定待检查文件
    file_path = "/install-package/RuoYi-Vue/ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysUserServiceImpl.java"
    #file_path = "/security/fdisk1/projects/JSH_ERP/jshERP-boot/src/main/java/com/jsh/erp/utils/ParamUtils.java"
    uri = "file://" + file_path
    line = 167
    character = 22
    lsp_client.initialize(p.pid, None, root_uri, None, capabilities,
                          "messages", workspace_folders)
    lsp_client.initialized()

    languageId = pylspclient.lsp_structs.LANGUAGE_IDENTIFIER.JAVA
    version = 0
    process_item(pylspclient, lsp_client, uri, languageId, version, file_path, line, character)
    file_path = "/install-package/RuoYi-Vue/ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysMenuServiceImpl.java"
    uri = "file://" + file_path
    process_item(pylspclient, lsp_client, uri, languageId, version, file_path, 227, 25)

    lsp_client.shutdown()
    lsp_client.exit()
