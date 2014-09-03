#!/bin/bash
cat test_request.txt && curl -v -A CsdTesting/Mozilla --data-binary @test_request.txt "http://localhost:8080/downloads?client=Firefox&appver=1&pver=2.2"
