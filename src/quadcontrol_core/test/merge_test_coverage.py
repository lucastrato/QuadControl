import argparse
import html
from pathlib import Path
import xml.etree.ElementTree as ElementTree


def render_html(report, output_path):
    test_cases = []
    test_results = report.find('test_results')
    for result in test_results.findall('test_result'):
        for test_case in result.iter('testcase'):
            if test_case.find('failure') is not None:
                status = 'failed'
            elif test_case.find('error') is not None:
                status = 'error'
            elif test_case.find('skipped') is not None:
                status = 'skipped'
            else:
                status = 'passed'

            details = ' '.join(
                text.strip()
                for element in test_case
                if element.tag in ('failure', 'error', 'skipped')
                for text in element.itertext()
                if text.strip()
            )
            test_cases.append(
                (
                    status,
                    test_case.get('classname', result.get('file', '')),
                    test_case.get('name', ''),
                    details,
                )
            )

    totals = {
        status: sum(test[0] == status for test in test_cases)
        for status in ('passed', 'failed', 'error', 'skipped')
    }
    coverage = report.find('./coverage_result/coverage')
    line_rate = float(coverage.get('line-rate', '0'))
    branch_rate = float(coverage.get('branch-rate', '0'))
    covered_lines = coverage.get('lines-covered', '0')
    total_lines = coverage.get('lines-valid', '0')
    covered_branches = coverage.get('branches-covered', '0')
    total_branches = coverage.get('branches-valid', '0')

    coverage_rows = []
    for class_element in coverage.findall('.//class'):
        class_line_rate = float(class_element.get('line-rate', '0'))
        class_branch_rate = float(class_element.get('branch-rate', '0'))
        filename = class_element.get(
            'filename',
            class_element.get('name', ''),
        )
        coverage_rows.append(
            '<tr><td>{}</td><td>{:.1%}</td><td>{:.1%}</td></tr>'.format(
                html.escape(filename),
                class_line_rate,
                class_branch_rate,
            )
        )

    test_rows = []
    for status, suite, name, details in test_cases:
        test_rows.append(
            '<tr data-test="{}"><td><span class="badge {}">{}</span></td>'
            '<td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                html.escape('{} {}'.format(suite, name).lower()),
                status,
                status,
                html.escape(suite),
                html.escape(name),
                html.escape(details),
            )
        )

    document = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>QuadControl Test and Coverage</title>
    <style>
                :root { color-scheme: light; font: 15px/1.5 system-ui, sans-serif;
                        color: #172b36; background: #f3f7f8; }
        body { margin: 0; }
        main { max-width: 1100px; margin: 0 auto; padding: 32px 20px 56px; }
        h1 { margin: 0; font-size: 1.8rem; }
        h2 { margin: 32px 0 12px; font-size: 1.2rem; }
        .subtitle { color: #536873; margin-top: 4px; }
                .metrics { display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
                        gap: 12px; margin-top: 24px; }
        .metric, section { background: white; border: 1px solid #d8e2e6; border-radius: 6px; }
        .metric { padding: 16px; }
        .metric span { display: block; color: #536873; font-size: .9rem; }
        .metric strong { display: block; font-size: 1.6rem; font-variant-numeric: tabular-nums; }
        section { padding: 16px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; }
                th, td { text-align: left; padding: 9px 10px;
                        border-bottom: 1px solid #e4ecef; vertical-align: top; }
        th { color: #536873; font-size: .85rem; }
        tr:last-child td { border-bottom: 0; }
                .badge { display: inline-block; border-radius: 999px;
                        padding: 2px 9px; font-size: .8rem; font-weight: 650; }
        .passed { color: #145c3b; background: #e3f5eb; }
        .failed, .error { color: #8d2530; background: #fde8e8; }
        .skipped { color: #725211; background: #fff3ce; }
                input { width: min(100%, 360px); box-sizing: border-box;
                        padding: 9px 11px; border: 1px solid #bdcbd1;
                        border-radius: 4px; font: inherit; }
                .toolbar { display: flex; justify-content: space-between;
                        gap: 12px; align-items: center; margin-bottom: 10px; }
        .muted { color: #536873; }
                @media (max-width: 600px) { main { padding: 22px 12px 40px; }
                        .toolbar { align-items: stretch; flex-direction: column; } }
    </style>
</head>
<body>
    <main>
        <h1>QuadControl Test and Coverage</h1>
        <div class="subtitle">Combined colcon test results and gcovr coverage report</div>
        <div class="metrics">
            <div class="metric"><span>Passed</span><strong>@@PASSED@@</strong></div>
                        <div class="metric"><span>Failed / errors</span>
                                <strong>@@FAILED@@ / @@ERRORS@@</strong></div>
            <div class="metric"><span>Skipped</span><strong>@@SKIPPED@@</strong></div>
                        <div class="metric"><span>Line coverage</span>
                                <strong>@@LINE_RATE@@</strong><span>@@LINES@@ lines</span></div>
                        <div class="metric"><span>Branch coverage</span>
                            <strong>@@BRANCH_RATE@@</strong>
                            <span>@@BRANCHES@@ branches</span></div>
        </div>
        <h2>Coverage by source file</h2>
        <section>
                        <table><thead>
                                <tr><th>File</th><th>Lines</th><th>Branches</th></tr>
                        </thead><tbody>@@COVERAGE_ROWS@@</tbody></table>
        </section>
        <h2>Test cases</h2>
        <section>
                        <div class="toolbar">
                                <span class="muted">Filter by suite or test name</span>
                                <input id="filter" type="search" placeholder="Filter tests"
                                        aria-label="Filter tests">
                        </div>
                        <table><thead>
                                <tr><th>Status</th><th>Suite</th><th>Test</th><th>Details</th></tr>
                        </thead><tbody id="tests">@@TEST_ROWS@@</tbody></table>
        </section>
    </main>
    <script>
        document.getElementById('filter').addEventListener('input', function () {
            const query = this.value.toLowerCase();
            document.querySelectorAll('#tests tr').forEach(function (row) {
                row.hidden = !row.dataset.test.includes(query);
            });
        });
    </script>
</body>
</html>
"""
    replacements = {
        '@@PASSED@@': str(totals['passed']),
        '@@FAILED@@': str(totals['failed']),
        '@@ERRORS@@': str(totals['error']),
        '@@SKIPPED@@': str(totals['skipped']),
        '@@LINE_RATE@@': '{:.1%}'.format(line_rate),
        '@@BRANCH_RATE@@': '{:.1%}'.format(branch_rate),
        '@@LINES@@': '{}/{}'.format(covered_lines, total_lines),
        '@@BRANCHES@@': '{}/{}'.format(covered_branches, total_branches),
        '@@COVERAGE_ROWS@@': '\n'.join(coverage_rows),
        '@@TEST_ROWS@@': '\n'.join(test_rows),
    }
    for placeholder, value in replacements.items():
        document = document.replace(placeholder, value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding='utf-8')
    print(f'HTML test and coverage dashboard: {output_path}')


def main():
    parser = argparse.ArgumentParser(
        description='Combine colcon test results and gcovr coverage into one XML report.'
    )
    parser.add_argument('--test-results-dir', type=Path, required=True)
    parser.add_argument('--coverage-xml', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--html-output', type=Path)
    arguments = parser.parse_args()

    test_reports = sorted(arguments.test_results_dir.glob('*.xml'))
    if not test_reports:
        parser.error(f'No test result XML files found in {arguments.test_results_dir}')
    if not arguments.coverage_xml.is_file():
        parser.error(f'Coverage XML file not found: {arguments.coverage_xml}')

    report = ElementTree.Element('quadcontrol_test_coverage_report', version='1')
    test_results = ElementTree.SubElement(report, 'test_results')
    for report_path in test_reports:
        result = ElementTree.SubElement(test_results, 'test_result', file=report_path.name)
        result.append(ElementTree.parse(report_path).getroot())

    coverage = ElementTree.SubElement(report, 'coverage_result', file=arguments.coverage_xml.name)
    coverage.append(ElementTree.parse(arguments.coverage_xml).getroot())

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    ElementTree.indent(report, space='  ')
    ElementTree.ElementTree(report).write(
        arguments.output,
        encoding='utf-8',
        xml_declaration=True,
    )
    print(f'Combined test and coverage report: {arguments.output}')
    if arguments.html_output is not None:
        render_html(report, arguments.html_output)


if __name__ == '__main__':
    main()
