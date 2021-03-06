
import logging
import azure.functions as func


def main(req: func.HttpRequest, connectionInfo) -> func.HttpResponse:
    return func.HttpResponse(connectionInfo, headers={'Access-Control-Allow-Origin': '*'})