package com.example.connections.adapter.in.http;

import com.example.connections.domain.exception.AuthorizationException;
import com.example.connections.domain.exception.DomainException;
import com.example.connections.domain.exception.NotFoundException;
import com.example.connections.domain.exception.StateException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    record ErrorResponse(String message) {}

    @ExceptionHandler(NotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    ErrorResponse handleNotFound(NotFoundException ex) {
        return new ErrorResponse(ex.getMessage());
    }

    @ExceptionHandler(AuthorizationException.class)
    @ResponseStatus(HttpStatus.FORBIDDEN)
    ErrorResponse handleAuthorization(AuthorizationException ex) {
        return new ErrorResponse(ex.getMessage());
    }

    @ExceptionHandler(StateException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    ErrorResponse handleState(StateException ex) {
        return new ErrorResponse(ex.getMessage());
    }

    @ExceptionHandler(DomainException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    ErrorResponse handleDomain(DomainException ex) {
        return new ErrorResponse(ex.getMessage());
    }
}
