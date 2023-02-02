const fs = require('fs');
const path = require('path');

const parser = require('@solidity-parser/parser');

const [,, outfile, ...infiles] = process.argv;
const fout = fs.createWriteStream(outfile, { flags: 'a' });

infiles.forEach(file => {
    const addr = path.basename(file, '.sol');
    const code = fs.readFileSync(file, 'utf8').replace(/&#39;/g, '\'');
    try {
        const ast = parser.parse(code, { loc: true, range: true });
        ast.children.forEach(child => {
            if(child.type === 'ContractDefinition') {
                const contract = child.name;
                const [start, end] = child.range; // current contract's source code [start, end + 1)
                const { start: startloc, end: endloc } = child.loc;
                const { line: sline, column: scol } = startloc;
                const { line: eline, column: ecol } = endloc;
                fout.write(`${addr},${contract},${start},${end},${sline},${scol},${eline},${ecol}\n`);
            }
        });
    } catch(e) {
        if(e instanceof parser.ParserError) {
            // TODO
        }
        console.error(e);
    }
});

fout.end();
